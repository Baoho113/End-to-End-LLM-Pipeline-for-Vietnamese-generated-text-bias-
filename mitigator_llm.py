"""
mitigator_llm.py — Stage 2: LLM-based bias rewriting for Vietnamese text.

Called only when:
  - Severity score is 3 (too severe for simple rule patching), OR
  - Rule-based mitigation ran but the detector still flags the text as biased.

Uses the Anthropic API with a carefully structured prompt that instructs
the model to rewrite for neutrality while preserving meaning and fluency.

Usage:
    from mitigator_llm import LLMMitigator
    m = LLMMitigator()
    result = m.mitigate(
        "Phụ nữ không nên làm giám đốc vì thiếu lý trí.",
        category="gender_stereotype",
        severity=3,
    )
    print(result.mitigated_text)
"""

import os
from mitigator_rules import MitigationResult


# ═══════════════════════════════════════════════════════════════════════════
#  Category context — tells the LLM what kind of bias to remove
# ═══════════════════════════════════════════════════════════════════════════

CATEGORY_DESCRIPTIONS = {
    "gender_stereotype": (
        "định kiến giới tính — nội dung gán vai trò, nghề nghiệp, hoặc đặc điểm "
        "tính cách cho một giới tính cụ thể một cách không công bằng"
    ),
    "regional_bias": (
        "định kiến vùng miền — nội dung khái quát hóa tiêu cực về người từ "
        "các tỉnh thành, vùng miền hoặc giọng địa phương cụ thể"
    ),
    "socioeconomic_occupation_bias": (
        "định kiến kinh tế xã hội — nội dung phân biệt đối xử dựa trên nghề nghiệp, "
        "trình độ học vấn, hoặc hoàn cảnh kinh tế của một người"
    ),
    "appearance_derogation": (
        "phân biệt ngoại hình — nội dung đánh giá hoặc phân biệt đối xử dựa trên "
        "ngoại hình, cân nặng, màu da, chiều cao hoặc đặc điểm thể chất"
    ),
}

SYSTEM_PROMPT = """Bạn là một chuyên gia viết lại nội dung tiếng Việt nhằm loại bỏ định kiến và thành kiến.
Nhiệm vụ của bạn là viết lại câu hoặc đoạn văn tiếng Việt để loại bỏ nội dung phân biệt đối xử,
đồng thời giữ nguyên ý nghĩa cốt lõi và văn phong tự nhiên của câu gốc.

Quy tắc bắt buộc:
1. Chỉ trả về câu đã được viết lại — không giải thích, không ghi chú, không tiêu đề.
2. Giữ nguyên ngôn ngữ tiếng Việt.
3. Đảm bảo câu viết lại tự nhiên, đúng ngữ pháp và không mang nghĩa tiêu cực.
4. Nếu câu gốc có thể được trung lập hóa hoàn toàn, hãy làm vậy.
5. Nếu câu gốc chứa thông tin thực sự có ích nhưng được diễn đạt sai, hãy giữ phần thông tin đó và sửa cách diễn đạt.
6. Không thêm nội dung mới không có trong câu gốc."""


def build_user_prompt(text: str, category: str, severity: int) -> str:
    """Build the rewrite prompt for the LLM."""
    category_desc = CATEGORY_DESCRIPTIONS.get(category, "nội dung có định kiến")
    severity_context = {
        1: "Câu này có dấu hiệu nhẹ của định kiến.",
        2: "Câu này chứa định kiến rõ ràng cần được sửa đổi.",
        3: "Câu này chứa định kiến nghiêm trọng và cần được viết lại hoàn toàn.",
    }.get(severity, "Câu này chứa định kiến.")

    return f"""Loại định kiến cần loại bỏ: {category_desc}

{severity_context}

Câu gốc:
\"{text}\"

Hãy viết lại câu trên để loại bỏ {category_desc}, giữ ý nghĩa trung lập và văn phong tự nhiên."""


# ═══════════════════════════════════════════════════════════════════════════
#  LLM mitigator
# ═══════════════════════════════════════════════════════════════════════════

class LLMMitigator:
    """
    Stage 2 mitigation using an LLM to rewrite biased Vietnamese text.

    Requires ANTHROPIC_API_KEY environment variable.
    Falls back gracefully if the API call fails.
    """

    def __init__(self, model: str = "claude-sonnet-4-20250514", max_tokens: int = 512):
        self.model = model
        self.max_tokens = max_tokens
        self._client = None

    @property
    def client(self):
        """Lazy-load the Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(
                    api_key=os.environ.get("ANTHROPIC_API_KEY")
                )
            except ImportError:
                raise RuntimeError(
                    "anthropic package not installed. Run: pip install anthropic"
                )
        return self._client

    def _call_api(self, text: str, category: str, severity: int) -> str:
        """Call the Anthropic API and return the rewritten text."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": build_user_prompt(text, category, severity),
                }
            ],
        )
        return response.content[0].text.strip().strip('"').strip("'")

    def mitigate(
        self,
        text: str,
        category: str,
        severity: int = 2,
        original_text: str = None,
    ) -> MitigationResult:
        """
        Rewrite biased text using the LLM.

        Args:
            text:          Text to rewrite (may be pre-processed by rule stage).
            category:      Detected bias category.
            severity:      Detected severity score (0–3).
            original_text: The original input before any rule processing.

        Returns:
            MitigationResult with LLM-rewritten text.
        """
        original = original_text or text

        try:
            rewritten = self._call_api(text, category, severity)
            return MitigationResult(
                original_text=original,
                mitigated_text=rewritten,
                category=category,
                stage="llm_rewrite",
                rules_applied=["LLM rewrite via Anthropic API"],
            )
        except Exception as e:
            print(f"  [LLM mitigator] API call failed: {e}. Returning rule-based output.")
            return MitigationResult(
                original_text=original,
                mitigated_text=text,
                category=category,
                stage="llm_rewrite_failed",
                rules_applied=[f"LLM failed: {str(e)}"],
            )

    def mitigate_batch(
        self,
        texts: list[str],
        categories: list[str],
        severities: list[int],
    ) -> list[MitigationResult]:
        """Rewrite a batch of texts."""
        results = []
        for i, (text, cat, sev) in enumerate(zip(texts, categories, severities)):
            print(f"  LLM rewriting [{i+1}/{len(texts)}]: {text[:50]}...")
            results.append(self.mitigate(text, cat, sev))
        return results
