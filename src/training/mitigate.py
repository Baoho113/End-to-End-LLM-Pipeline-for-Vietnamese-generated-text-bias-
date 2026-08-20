"""AI rewriting for flagged text, using an OpenAI-compatible chat API.

Task 4 from docs/task_definition.md ("Bias Mitigation Generation" / safer_text)
done with a hosted LLM instead of a fine-tuned ViT5 -- that's the v2/severity
track's job. Takes a sentence plus its detected category from
inference_test.predict() and asks a chat model to rewrite it into neutral
Vietnamese while preserving the original meaning.

Talks to RMIT's VAL gateway (an OpenAI-compatible proxy) by default, not
OpenAI's own api.openai.com -- that's what the "VAL-Balam-Key1" Bitwarden item
is scoped to. Override OPENAI_BASE_URL to point at a different OpenAI-
compatible endpoint (e.g. unset it, or set it to OpenAI's own API, if you're
using a personal OpenAI account key instead).

The OpenAI key isn't stored in .env -- it's pulled from the local Bitwarden
vault via the `bw` CLI. `bw` must already be logged in and unlocked (BW_SESSION
set in this process's environment); this deliberately doesn't attempt an
interactive `bw unlock`, since a server process has no way to satisfy a master
password prompt. See README for the one-time `bw login` / `bw unlock` steps.

CLI usage (manual testing, independent of the FastAPI service):
    Just check the key resolves (no OpenAI call, no tokens spent):
        python mitigate.py

    Full rewrite round trip:
        python mitigate.py "Người già thường khó tiếp thu." --label "Age Bias"
"""

import argparse
import json
import os
import shutil
import subprocess
from functools import lru_cache

from openai import OpenAI

BW_ITEM_NAME = os.environ.get("OPENAI_BW_ITEM", "VAL-Balam-Key1")
MITIGATION_MODEL = os.environ.get("MITIGATION_MODEL", "openai-gpt-4o")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://val.rmit.edu.au/api/")

SYSTEM_PROMPT = (
    "Bạn là một biên tập viên trung lập. Nhiệm vụ của bạn là viết lại câu "
    "tiếng Việt do người dùng cung cấp để loại bỏ định kiến/thiên vị, trong "
    "khi vẫn giữ nguyên ý nghĩa và thông tin cốt lõi của câu gốc. Chỉ trả về "
    "câu đã viết lại, không thêm giải thích, không thêm dấu ngoặc kép."
)


@lru_cache(maxsize=1)
def _get_api_key() -> str:
    """Resolves the OpenAI key: OPENAI_API_KEY env var first (explicit
    override / CI), otherwise `bw get password <BW_ITEM_NAME>`.
    """
    env_override = os.environ.get("OPENAI_API_KEY")
    if env_override:
        return env_override

    bw_path = shutil.which("bw")
    if bw_path is None:
        raise RuntimeError(
            "Bitwarden CLI ('bw') not found on PATH. Install it "
            "(https://bitwarden.com/help/cli/) and `bw login`, or set "
            "OPENAI_API_KEY directly to bypass Bitwarden."
        )

    try:
        result = subprocess.run(
            [bw_path, "get", "password", BW_ITEM_NAME],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"`bw get password {BW_ITEM_NAME}` failed -- is the vault unlocked "
            "(BW_SESSION set in this shell)? Run `bw unlock` and export the "
            f"session key it prints. stderr: {exc.stderr.strip()}"
        ) from exc

    key = result.stdout.strip()
    if not key:
        raise RuntimeError(f"Bitwarden item '{BW_ITEM_NAME}' returned an empty password.")
    return key


@lru_cache(maxsize=1)
def _get_client() -> OpenAI:
    if OPENAI_BASE_URL:
        return OpenAI(api_key=_get_api_key(), base_url=OPENAI_BASE_URL.rstrip("/"))
    return OpenAI(api_key=_get_api_key())


def mitigate(text: str, label: str | None = None) -> dict:
    """Rewrites `text` into a safer, non-biased version.

    `label` is the detected bias category (e.g. "Gender Bias") -- passed
    through as context so the model targets that specific bias rather than
    generically paraphrasing.
    """
    client = _get_client()

    category_hint = f" Loại định kiến đã phát hiện: {label}." if label and label != "Non-bias" else ""
    user_prompt = (
        "Viết lại câu sau để loại bỏ định kiến, giữ nguyên ý nghĩa cốt lõi."
        f"{category_hint}\n\nCâu gốc: {text}"
    )

    try:
        response = client.chat.completions.create(
            model=MITIGATION_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
    except Exception as exc:
        raise RuntimeError(f"OpenAI mitigation request failed: {exc}") from exc

    safer_text = response.choices[0].message.content.strip()

    return {
        "original_text": text,
        "safer_text": safer_text,
        "label": label,
        "model": MITIGATION_MODEL,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "text", nargs="?", help="Sentence to rewrite; omit to only test that the API key resolves"
    )
    parser.add_argument("--label", help="Detected bias category to pass as context, e.g. 'Gender Bias'")
    args = parser.parse_args()

    key = _get_api_key()
    masked = f"{key[:7]}...{key[-4:]}" if len(key) > 11 else "***"
    print(f"Resolved OpenAI key: {masked} ({len(key)} chars) -- source: "
          f"{'OPENAI_API_KEY env var' if os.environ.get('OPENAI_API_KEY') else f'Bitwarden item {BW_ITEM_NAME!r}'}")

    if args.text:
        print(f"Base URL: {OPENAI_BASE_URL or '(OpenAI default: api.openai.com)'}")
        print(f"Model: {MITIGATION_MODEL}")
        result = mitigate(args.text, label=args.label)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
