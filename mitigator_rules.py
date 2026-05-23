"""
mitigator_rules.py — Stage 1: Rule-based bias mitigation for Vietnamese text.

Applies fast, deterministic text transformations to reduce bias.
No API calls. No latency. Handles the easy majority of cases.

Techniques:
  1. Bias lexicon replacement   — swap flagged words/phrases with neutral ones
  2. Occupation–gender decoupling — remove gendered markers from job contexts
  3. Absolute qualifier softening — weaken "never/always/cannot" claims
  4. Regional generalisation removal — strip direct ethnic/regional stereotypes

Usage:
    from mitigator_rules import RuleBasedMitigator
    m = RuleBasedMitigator()
    result = m.mitigate("Phụ nữ không nên làm giám đốc.", "gender_stereotype")
    print(result.mitigated_text)
"""

import re
from dataclasses import dataclass, field


# ═══════════════════════════════════════════════════════════════════════════
#  Lexicons — category-specific word/phrase replacements
# ═══════════════════════════════════════════════════════════════════════════

# Format: (pattern_to_match, replacement, description)
# Patterns are applied in order — more specific patterns first.

GENDER_RULES = [
    # Occupational gendering — strip gender from job descriptions
    (r"phụ nữ\s+(?:thì\s+)?(?:nên|phù hợp|chỉ nên)\s+làm\s+(\w[\w\s]*)",
     r"người lao động có thể làm \1",
     "Remove occupational gender prescription"),
    (r"đàn ông\s+(?:thì\s+)?(?:nên|phù hợp|chỉ nên)\s+làm\s+(\w[\w\s]*)",
     r"người lao động có thể làm \1",
     "Remove occupational gender prescription"),
    (r"(?:công việc|nghề|vị trí)\s+(?:này\s+)?(?:chỉ\s+)?(?:dành cho|phù hợp với)\s+phụ nữ",
     "vị trí này phù hợp với người có kỹ năng phù hợp",
     "Neutralise gender-exclusive job framing"),
    (r"(?:công việc|nghề|vị trí)\s+(?:này\s+)?(?:chỉ\s+)?(?:dành cho|phù hợp với)\s+đàn ông",
     "vị trí này phù hợp với người có kỹ năng phù hợp",
     "Neutralise gender-exclusive job framing"),

    # Leadership & decision-making stereotypes
    (r"phụ nữ\s+(?:thường\s+)?(?:thiếu|không đủ|không có)\s+(?:bản lĩnh|quyết đoán|tầm nhìn|lý trí)",
     "mỗi cá nhân có phong cách lãnh đạo riêng",
     "Remove female leadership deficit framing"),
    (r"đàn ông\s+(?:thường\s+)?(?:quyết đoán|mạnh mẽ|lý trí)\s+hơn\s+phụ nữ",
     "khả năng lãnh đạo phụ thuộc vào cá nhân, không phải giới tính",
     "Remove male leadership superiority claim"),

    # Domestic role stereotypes
    (r"(?:đàn ông|con trai)\s+(?:mà\s+)?(?:làm|nấu|dọn)\s+(?:nội trợ|bếp|nhà)\s+(?:thì\s+)?(?:kỳ lạ|không phù hợp|thật lạ)",
     "việc chia sẻ công việc gia đình là điều bình thường",
     "Neutralise domestic role stigma for men"),
    (r"phụ nữ\s+(?:phải|nên|cần)\s+(?:biết|lo|chăm)\s+(?:nấu ăn|gia đình|con cái)",
     "mỗi người có thể đóng góp cho gia đình theo cách riêng của mình",
     "Neutralise domestic obligation framing for women"),

    # Emotional stereotypes
    (r"phụ nữ\s+(?:thường\s+)?(?:dễ|hay|quá)\s+(?:xúc động|cảm xúc|khóc)",
     "cảm xúc là phản ứng tự nhiên của con người",
     "Remove female emotionality stereotype"),
    (r"đàn ông\s+(?:không được|không nên|không thể)\s+khóc",
     "mỗi người có quyền thể hiện cảm xúc của mình",
     "Remove male emotional suppression norm"),
]

REGIONAL_RULES = [
    # Direct character generalisations about regions
    (r"(?:người|dân)\s+(miền [A-ZÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬ][a-zA-ZÀ-ỹ]+|Hà Nội|Sài Gòn|miền Trung|miền Nam|miền Bắc|miền Tây|Tây Nguyên)\s+(?:thường\s+)?(?:là|đều|hay|luôn)\s+(?:[a-zA-ZÀ-ỹ\s]+(?:lười|bảo thủ|kém|thô|hung hãn|thiếu|không có|cứng đầu|lạc hậu)[a-zA-ZÀ-ỹ\s]*)",
     r"người từ các vùng miền khác nhau có đặc điểm văn hóa riêng",
     "Remove negative regional character generalisation"),

    # Accent/dialect stigma
    (r"giọng\s+(?:[A-ZÀ-ỹ][a-zA-ZÀ-ỹ\s]+)\s+(?:nghe\s+)?(?:khó chịu|không hay|khó nghe|kém|không chuyên nghiệp|thô)",
     "mỗi giọng địa phương đều có nét đặc trưng riêng",
     "Neutralise accent stigma"),
    (r"giọng\s+(?:chuẩn|đẹp|hay)\s+(?:là|nhất)\s+(?:giọng\s+)?(?:Hà Nội|miền Bắc)",
     "không có giọng địa phương nào được coi là chuẩn mực duy nhất",
     "Remove single-dialect standard framing"),

    # Urban vs rural
    (r"(?:người|dân)\s+(?:tỉnh lẻ|nông thôn|vùng cao|vùng sâu)\s+(?:thường\s+)?(?:kém|thiếu|không|lạc hậu|chậm)",
     "người từ các địa phương khác nhau đều có những đóng góp giá trị",
     "Neutralise rural inferiority framing"),
    (r"dân\s+(?:thành phố|Hà Nội|thành thị)\s+(?:hơn|tốt hơn|giỏi hơn|chuyên nghiệp hơn)\s+dân\s+(?:tỉnh|nông thôn|quê)",
     "năng lực cá nhân không phụ thuộc vào nơi sinh sống",
     "Remove urban superiority claim"),
]

SOCIOECONOMIC_RULES = [
    # Education-based dismissal
    (r"(?:người|ai)\s+(?:không có|thiếu|chỉ có)\s+(?:bằng|học vấn|trình độ)\s+(?:đại học|cao)?\s+(?:thì\s+)?(?:không thể|không nên|không đủ|không xứng)",
     "trình độ học vấn không phải là thước đo duy nhất của năng lực",
     "Remove education-credential gatekeeping"),

    # Occupation-based character judgements
    (r"(?:người|thợ|dân)\s+(?:làm\s+)?(?:lao động|công nhân|nghề tay chân|lao động phổ thông|ve chai|bảo vệ|tạp vụ|phụ hồ)\s+(?:thường\s+)?(?:không|thiếu|kém|không đáng|không xứng)",
     "người lao động ở mọi lĩnh vực đều đáng được tôn trọng",
     "Remove manual labour dignity dismissal"),

    # Income-to-character attribution
    (r"(?:người|gia đình)\s+(?:nghèo|thu nhập thấp|không có tiền)\s+(?:thường\s+)?(?:thiếu|không biết|kém|không có)",
     "hoàn cảnh kinh tế không quyết định phẩm chất hay năng lực của một người",
     "Remove poverty-to-character attribution"),

    # Class-based trust dismissal
    (r"(?:người|ai)\s+(?:làm\s+)?(?:ve chai|bán hàng rong|đánh giày|lái xe ôm|shipper)\s+(?:thường\s+)?(?:không đáng tin|không tin tưởng|không đáng)",
     "sự tin tưởng được xây dựng qua hành động, không phải nghề nghiệp",
     "Remove occupation-based trust deficit"),
]

APPEARANCE_RULES = [
    # Weight-based dismissal
    (r"(?:người|nhân viên|ứng viên)\s+(?:béo|thừa cân|mập)\s+(?:thường\s+)?(?:không nên|không phù hợp|trông|làm giảm|thiếu)",
     "ngoại hình không nên là tiêu chí đánh giá năng lực làm việc",
     "Remove weight-based professional dismissal"),

    # Skin colour bias
    (r"da\s+(?:đen|ngăm|ngăm đen)\s+(?:thì\s+)?(?:không|kém|ít|trông không)",
     "màu da không ảnh hưởng đến năng lực hay giá trị của một người",
     "Remove skin colour bias"),
    (r"da\s+(?:trắng|sáng)\s+(?:thì\s+)?(?:hơn|đẹp hơn|sang hơn|tốt hơn)",
     "mọi màu da đều có giá trị như nhau",
     "Remove skin colour hierarchy"),

    # Tattoo stigma
    (r"(?:người|ứng viên|nhân viên)\s+(?:có|mang)\s+(?:hình\s+)?xăm\s+(?:thường\s+)?(?:là|bị coi là|thường bị|không phù hợp|không nên)",
     "hình xăm không phản ánh năng lực hay tính cách của một người",
     "Remove tattoo stigma"),

    # Height discrimination
    (r"(?:người|đàn ông|ứng viên)\s+(?:thấp|không cao|lùn)\s+(?:thường\s+)?(?:bị|không|khó|thiếu)",
     "chiều cao không quyết định năng lực hay uy tín của một người",
     "Remove height-based discrimination"),

    # Appearance as hiring criterion
    (r"(?:ứng viên|nhân viên)\s+(?:ngoại hình\s+)?(?:xấu|kém|bình thường|không đẹp)\s+(?:thì\s+)?(?:khó|không|không nên|nên tránh)",
     "tuyển dụng nên dựa trên năng lực và kinh nghiệm",
     "Remove appearance-based hiring bias"),
]

# Absolute qualifier softening — apply across all categories
ABSOLUTE_QUALIFIERS = [
    (r"\bkhông bao giờ\s+(?:có thể|được|nên)\b", "hiếm khi hoặc khó có thể", "Soften absolute negation"),
    (r"\bchắc chắn\s+(?:là\s+)?không\b", "thường không", "Soften certainty negation"),
    (r"\bhoàn toàn\s+không\b", "ít khi", "Soften absolute negation"),
    (r"\bkhông thể nào\b", "khó có thể", "Soften impossibility claim"),
    (r"\bđương nhiên là\b", "có thể", "Soften naturalisation claim"),
    (r"\bai cũng biết rằng\b", "một số người cho rằng", "Soften false consensus"),
    (r"\bthực tế là\b", "theo một số quan điểm,", "Soften false-fact framing"),
    (r"\bđó là quy luật\b", "đó là một quan điểm", "Soften naturalisation"),
    (r"\btất cả (?:mọi người đều biết|đều thấy|đều nhận thấy)\b", "nhiều người cho rằng", "Soften false consensus"),
    (r"\bhầu hết (?:phụ nữ|đàn ông|người nghèo|dân tỉnh|công nhân)\s+đều\b",
     r"một số \g<0>".replace(r"\b.*\b", ""),
     "Soften sweeping generalisation"),
]

# Map category to its ruleset
CATEGORY_RULES = {
    "gender_stereotype": GENDER_RULES,
    "regional_bias": REGIONAL_RULES,
    "socioeconomic_occupation_bias": SOCIOECONOMIC_RULES,
    "appearance_derogation": APPEARANCE_RULES,
}


# ═══════════════════════════════════════════════════════════════════════════
#  Result dataclass
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class MitigationResult:
    original_text: str
    mitigated_text: str
    category: str
    stage: str                         # "rule_based" | "llm_rewrite" | "none"
    rules_applied: list[str] = field(default_factory=list)
    changed: bool = False

    def __post_init__(self):
        self.changed = self.original_text.strip() != self.mitigated_text.strip()

    def to_dict(self):
        return {
            "original_text": self.original_text,
            "mitigated_text": self.mitigated_text,
            "category": self.category,
            "stage": self.stage,
            "rules_applied": self.rules_applied,
            "changed": self.changed,
        }


# ═══════════════════════════════════════════════════════════════════════════
#  Rule-based mitigator
# ═══════════════════════════════════════════════════════════════════════════

class RuleBasedMitigator:
    """
    Fast deterministic mitigation using regex-based lexicon replacement.

    Applies category-specific rules first, then softens absolute
    qualifiers that remain. All rules are applied case-insensitively.
    """

    def _apply_rules(self, text: str, rules: list[tuple]) -> tuple[str, list[str]]:
        """Apply a list of (pattern, replacement, description) rules."""
        applied = []
        for pattern, replacement, description in rules:
            try:
                new_text, n = re.subn(pattern, replacement, text, flags=re.IGNORECASE)
                if n > 0:
                    text = new_text
                    applied.append(description)
            except re.error:
                continue
        return text, applied

    def mitigate(self, text: str, category: str) -> MitigationResult:
        """
        Apply rule-based mitigation to a single text.

        Args:
            text:     The biased Vietnamese text to mitigate.
            category: The detected bias category from the detector.

        Returns:
            MitigationResult with mitigated text and applied rules log.
        """
        applied = []

        # Step 1: Category-specific rules
        cat_rules = CATEGORY_RULES.get(category, [])
        text, cat_applied = self._apply_rules(text, cat_rules)
        applied.extend(cat_applied)

        # Step 2: Universal absolute qualifier softening
        text, qual_applied = self._apply_rules(text, ABSOLUTE_QUALIFIERS)
        applied.extend(qual_applied)

        return MitigationResult(
            original_text=text if not applied else MitigationResult.__dataclass_fields__["original_text"].default,
            mitigated_text=text,
            category=category,
            stage="rule_based",
            rules_applied=applied,
        )

    def mitigate_batch(self, texts: list[str], categories: list[str]) -> list[MitigationResult]:
        """Mitigate a batch of texts."""
        return [self.mitigate(t, c) for t, c in zip(texts, categories)]


# ═══════════════════════════════════════════════════════════════════════════
#  Correct the dataclass — original_text needs to be set before mutation
# ═══════════════════════════════════════════════════════════════════════════

class RuleBasedMitigator(RuleBasedMitigator):
    """Fixed version that correctly tracks original text."""

    def mitigate(self, text: str, category: str) -> MitigationResult:
        original = text
        applied = []

        cat_rules = CATEGORY_RULES.get(category, [])
        text, cat_applied = self._apply_rules(text, cat_rules)
        applied.extend(cat_applied)

        text, qual_applied = self._apply_rules(text, ABSOLUTE_QUALIFIERS)
        applied.extend(qual_applied)

        return MitigationResult(
            original_text=original,
            mitigated_text=text,
            category=category,
            stage="rule_based",
            rules_applied=applied,
        )
