#!/usr/bin/env python3
"""
Meeting Notes Validator
=======================
Validates meeting notes markdown files for completeness, formatting correctness,
and cross-reference consistency.

Usage:
    python validate_notes.py <meeting-notes.md>
    python validate_notes.py <meeting-notes.md> --lang zh_TW
    python validate_notes.py <meeting-notes.md> --json
    python validate_notes.py <meeting-notes.md> --transcript <transcript.txt>
    python validate_notes.py <meeting-notes.md> --transcript <transcript.txt> --glossary <glossary.md>
    python validate_notes.py <meeting-notes.md> --participants '王小明,李小華,陳大同'
    python validate_notes.py <meeting-notes.md> --participants attendees.txt
"""

import re
import sys
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional


class Severity(str, Enum):
    PASS = "pass"
    WARNING = "warning"
    ERROR = "error"


class Category(str, Enum):
    METADATA = "metadata"
    PARTICIPANTS = "participants"
    AGENDA = "agenda"
    DISCUSSION = "discussion"
    ACTION_ITEMS = "action_items"
    STRUCTURE = "structure"
    CROSS_REFERENCE = "cross_reference"
    TRANSCRIPT_COVERAGE = "transcript_coverage"


@dataclass
class ValidationResult:
    severity: Severity
    category: Category
    message_zh: str
    message_en: str

    def display(self, lang: str = "zh_TW") -> str:
        icons = {
            Severity.PASS: "✅",
            Severity.WARNING: "⚠️",
            Severity.ERROR: "❌",
        }
        icon = icons[self.severity]
        label_map = {
            ("zh_TW", Severity.PASS): "通過",
            ("zh_TW", Severity.WARNING): "警告",
            ("zh_TW", Severity.ERROR): "錯誤",
            ("en", Severity.PASS): "PASS",
            ("en", Severity.WARNING): "WARNING",
            ("en", Severity.ERROR): "ERROR",
        }
        label = label_map.get((lang, self.severity), self.severity.value)
        msg = self.message_zh if lang == "zh_TW" else self.message_en
        return f"{icon} {label}: {msg}"


@dataclass
class ValidationReport:
    results: list[ValidationResult] = field(default_factory=list)
    file_path: str = ""

    def add(self, result: ValidationResult):
        self.results.append(result)

    @property
    def pass_count(self) -> int:
        return sum(1 for r in self.results if r.severity == Severity.PASS)

    @property
    def warning_count(self) -> int:
        return sum(1 for r in self.results if r.severity == Severity.WARNING)

    @property
    def error_count(self) -> int:
        return sum(1 for r in self.results if r.severity == Severity.ERROR)

    def display(self, lang: str = "zh_TW") -> str:
        lines = []
        if lang == "zh_TW":
            lines.append(f"## 📋 會議紀錄驗證報告")
            lines.append(f"")
            lines.append(f"**檔案**: `{self.file_path}`")
        else:
            lines.append(f"## 📋 Meeting Notes Validation Report")
            lines.append(f"")
            lines.append(f"**File**: `{self.file_path}`")
        lines.append("")

        # Group by category
        categories_zh = {
            Category.METADATA: "會議基本資訊",
            Category.PARTICIPANTS: "與會人員",
            Category.AGENDA: "會議議程",
            Category.DISCUSSION: "討論內容",
            Category.ACTION_ITEMS: "待辦事項",
            Category.STRUCTURE: "模板結構",
            Category.CROSS_REFERENCE: "交叉驗證",
            Category.TRANSCRIPT_COVERAGE: "逐字稿覆蓋率",
        }
        categories_en = {
            Category.METADATA: "Meeting Metadata",
            Category.PARTICIPANTS: "Participants",
            Category.AGENDA: "Agenda",
            Category.DISCUSSION: "Discussion",
            Category.ACTION_ITEMS: "Action Items",
            Category.STRUCTURE: "Template Structure",
            Category.CROSS_REFERENCE: "Cross-Reference",
            Category.TRANSCRIPT_COVERAGE: "Transcript Coverage",
        }
        cat_labels = categories_zh if lang == "zh_TW" else categories_en

        for cat in Category:
            cat_results = [r for r in self.results if r.category == cat]
            if cat_results:
                lines.append(f"### {cat_labels[cat]}")
                for r in cat_results:
                    lines.append(f"- {r.display(lang)}")
                lines.append("")

        # Summary
        lines.append("---")
        if lang == "zh_TW":
            lines.append(
                f"**總計**: {self.pass_count} 項通過, "
                f"{self.warning_count} 項警告, "
                f"{self.error_count} 項錯誤"
            )
        else:
            lines.append(
                f"**Total**: {self.pass_count} passed, "
                f"{self.warning_count} warnings, "
                f"{self.error_count} errors"
            )

        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps(
            {
                "file": self.file_path,
                "summary": {
                    "pass": self.pass_count,
                    "warning": self.warning_count,
                    "error": self.error_count,
                },
                "results": [
                    {
                        "severity": r.severity.value,
                        "category": r.category.value,
                        "message_zh": r.message_zh,
                        "message_en": r.message_en,
                    }
                    for r in self.results
                ],
            },
            ensure_ascii=False,
            indent=2,
        )


# ---------------------------------------------------------------------------
# Detection helpers
# ---------------------------------------------------------------------------

DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")
PLACEHOLDER_PATTERNS = [
    re.compile(r"\[.*?\]"),  # [placeholder text]
    re.compile(r"YYYY-MM-DD"),
    re.compile(r"HH:MM"),
]

# Bilingual section headers (EN and zh_TW)
REQUIRED_SECTIONS = {
    "metadata": [
        # EN
        r"Meeting\s+(Title|Information)",
        r"會議(名稱|基本資訊)",
    ],
    "participants": [
        r"Attend|Present",
        r"出席人員|與會人員",
    ],
    "agenda": [
        r"Agenda",
        r"會議議程|議程",
    ],
    "discussion": [
        r"Meeting\s+Summary|Discussion",
        r"會議內容摘要|會議內容",
    ],
    "next_meeting": [
        r"Next\s+Meeting",
        r"下次會議",
    ],
}

ACTION_ITEM_PATTERN_EN = re.compile(
    r"- \[[ x]\]\s+(.+?)(?:\s*-\s*Owner:\s*(.+?))?\s*(?:-\s*Due:\s*(\S+))?\s*$",
    re.MULTILINE,
)
ACTION_ITEM_PATTERN_ZH = re.compile(
    r"- \[[ x]\]\s+(.+?)(?:\s*-\s*負責人:\s*(.+?))?\s*(?:-\s*期限:\s*(\S+))?\s*$",
    re.MULTILINE,
)


def detect_language(content: str) -> str:
    """Detect whether the meeting notes are primarily zh_TW or EN."""
    zh_markers = ["會議", "議程", "出席", "決議", "待辦", "負責人", "期限", "主持人"]
    zh_count = sum(1 for m in zh_markers if m in content)
    return "zh_TW" if zh_count >= 3 else "en"


def extract_participants(content: str) -> list[str]:
    """Extract participant names from the attendee sections."""
    names: list[str] = []
    in_participant_section = False

    for line in content.splitlines():
        # Detect participant section headers
        if re.search(r"(出席人員|Present|Attend|與會人員|請假人員|On Leave|缺席人員|Absent)", line, re.IGNORECASE):
            in_participant_section = True
            continue

        # Detect end of participant sections
        if in_participant_section and line.startswith("## "):
            in_participant_section = False
            continue

        if in_participant_section and line.strip().startswith("- "):
            name_part = line.strip().lstrip("- ").split("-")[0].strip()
            # Skip placeholders
            if name_part and not re.match(r"^\[.*\]$", name_part):
                names.append(name_part)

    return names


def extract_action_item_owners(content: str) -> list[str]:
    """Extract responsible person names from action items."""
    owners: list[str] = []
    for pattern in [ACTION_ITEM_PATTERN_EN, ACTION_ITEM_PATTERN_ZH]:
        for match in pattern.finditer(content):
            owner = match.group(2)
            if owner and not re.match(r"^\[.*\]$", owner.strip()):
                owners.append(owner.strip())
    return owners


def load_provided_participants(participants_arg: str) -> list[str]:
    """Load user-provided participant list.

    Accepts either:
      - A file path (one name per line)
      - A comma-separated string of names
    """
    path = Path(participants_arg)
    if path.exists() and path.is_file():
        content = path.read_text(encoding="utf-8")
        names = [line.strip().lstrip("- ").strip()
                 for line in content.splitlines()
                 if line.strip() and not line.strip().startswith("#")]
        return [n for n in names if n]

    # Treat as comma-separated inline list
    names = [n.strip() for n in re.split(r"[,、，]", participants_arg) if n.strip()]
    return names


def has_placeholder(text: str) -> bool:
    """Check if text contains obvious placeholder content."""
    for p in PLACEHOLDER_PATTERNS:
        if p.search(text):
            return True
    return False


# ---------------------------------------------------------------------------
# Validation checks
# ---------------------------------------------------------------------------

def validate_metadata(content: str, report: ValidationReport):
    """Check meeting metadata fields are present and filled in."""
    doc_lang = detect_language(content)

    # Required metadata fields (bilingual)
    metadata_fields = {
        "meeting_title": (
            [r"\*\*Meeting Title\*\*:\s*(.+)", r"\*\*會議名稱\*\*:\s*(.+)"],
            "會議名稱已填寫", "Meeting title is filled in",
            "會議名稱為空或為佔位符", "Meeting title is empty or placeholder",
        ),
        "date": (
            [r"\*\*(Date|會議日期)\*\*:\s*(.+)"],
            "會議日期已填寫", "Meeting date is filled in",
            "會議日期為空或為佔位符", "Meeting date is empty or placeholder",
        ),
        "time": (
            [r"\*\*(Time|會議時間)\*\*:\s*(.+)"],
            "會議時間已填寫", "Meeting time is filled in",
            "會議時間為空或為佔位符", "Meeting time is empty or placeholder",
        ),
        "location": (
            [r"\*\*(Location|會議地點)\*\*:\s*(.+)"],
            "會議地點已填寫", "Meeting location is filled in",
            "會議地點為空或為佔位符", "Meeting location is empty or placeholder",
        ),
        "chairperson": (
            [r"\*\*(Chairperson|主持人)\*\*:\s*(.+)"],
            "主持人已填寫", "Chairperson is filled in",
            "主持人為空或為佔位符", "Chairperson is empty or placeholder",
        ),
        "recorder": (
            [r"\*\*(Recorder|記錄人)\*\*:\s*(.+)"],
            "記錄人已填寫", "Recorder is filled in",
            "記錄人為空或為佔位符", "Recorder is empty or placeholder",
        ),
    }

    for field_name, (patterns, msg_zh_pass, msg_en_pass, msg_zh_fail, msg_en_fail) in metadata_fields.items():
        found = False
        is_placeholder = False
        for pat in patterns:
            match = re.search(pat, content)
            if match:
                found = True
                value = match.group(match.lastindex)
                if has_placeholder(value):
                    is_placeholder = True
                break

        if found and not is_placeholder:
            report.add(ValidationResult(Severity.PASS, Category.METADATA, msg_zh_pass, msg_en_pass))
        else:
            report.add(ValidationResult(Severity.ERROR, Category.METADATA, msg_zh_fail, msg_en_fail))

    # Validate date format
    date_match = re.search(r"\*\*(Date|會議日期)\*\*:\s*(.+)", content)
    if date_match:
        date_val = date_match.group(2).strip()
        if DATE_PATTERN.fullmatch(date_val):
            report.add(ValidationResult(
                Severity.PASS, Category.METADATA,
                "日期格式正確 (YYYY-MM-DD)", "Date format is correct (YYYY-MM-DD)"
            ))
        elif not has_placeholder(date_val):
            report.add(ValidationResult(
                Severity.WARNING, Category.METADATA,
                f"日期格式建議使用 YYYY-MM-DD，目前為: {date_val}",
                f"Date format should be YYYY-MM-DD, got: {date_val}"
            ))


def validate_participants(content: str, report: ValidationReport,
                         provided_participants: Optional[list[str]] = None):
    """Check participant sections and verify against user-provided list."""
    participants = extract_participants(content)

    if len(participants) > 0:
        report.add(ValidationResult(
            Severity.PASS, Category.PARTICIPANTS,
            f"已列出 {len(participants)} 位與會人員",
            f"Found {len(participants)} participant(s) listed"
        ))
    else:
        report.add(ValidationResult(
            Severity.ERROR, Category.PARTICIPANTS,
            "未找到任何與會人員（出席人員清單為空或皆為佔位符）",
            "No participants found (attendee list is empty or all placeholders)"
        ))

    # Cross-check against user-provided participant list
    if provided_participants:
        notes_participants_set = {p.strip() for p in participants}
        for name in provided_participants:
            if name in notes_participants_set:
                report.add(ValidationResult(
                    Severity.PASS, Category.PARTICIPANTS,
                    f"指定出席者「{name}」已記錄在會議紀錄中",
                    f"Specified attendee \"{name}\" is recorded in meeting notes"
                ))
            else:
                # Check if partially present in content (e.g. in discussion body)
                if name in content:
                    report.add(ValidationResult(
                        Severity.WARNING, Category.PARTICIPANTS,
                        f"指定出席者「{name}」出現在內文但未列入出席人員名單",
                        f"Specified attendee \"{name}\" appears in content but NOT in participant list"
                    ))
                else:
                    report.add(ValidationResult(
                        Severity.WARNING, Category.PARTICIPANTS,
                        f"指定出席者「{name}」未出現在會議紀錄中",
                        f"Specified attendee \"{name}\" is NOT found in meeting notes"
                    ))

        # Also check if notes have participants not in the provided list
        provided_set = set(provided_participants)
        for p in participants:
            if p not in provided_set:
                report.add(ValidationResult(
                    Severity.WARNING, Category.PARTICIPANTS,
                    f"會議紀錄中的「{p}」不在指定出席名單中，請確認是否正確",
                    f"\"{p}\" in meeting notes is NOT in the provided attendee list — please verify"
                ))


def validate_agenda(content: str, report: ValidationReport):
    """Check agenda items exist."""
    # Look for numbered list items after agenda header
    agenda_section = False
    agenda_items = []
    for line in content.splitlines():
        if re.search(r"(##\s*(Agenda|會議議程))", line, re.IGNORECASE):
            agenda_section = True
            continue
        if agenda_section and line.startswith("## "):
            break
        if agenda_section and re.match(r"\d+\.\s+", line.strip()):
            item_text = re.sub(r"^\d+\.\s+", "", line.strip())
            if not re.match(r"^\[.*\]$", item_text):
                agenda_items.append(item_text)

    if len(agenda_items) > 0:
        report.add(ValidationResult(
            Severity.PASS, Category.AGENDA,
            f"已列出 {len(agenda_items)} 項議程",
            f"Found {len(agenda_items)} agenda item(s)"
        ))
    else:
        report.add(ValidationResult(
            Severity.WARNING, Category.AGENDA,
            "未找到實際議程項目（可能皆為佔位符）",
            "No actual agenda items found (may all be placeholders)"
        ))


def validate_discussion(content: str, report: ValidationReport):
    """Check discussion sections have content."""
    # Find topic headers (### [Topic X: ...] or ### [議題X: ...])
    topic_pattern = re.compile(r"###\s+(.+)")
    topics = []
    current_topic: Optional[str] = None
    current_content_lines: list[str] = []

    for line in content.splitlines():
        topic_match = topic_pattern.match(line)
        if topic_match:
            # Save previous topic
            if current_topic is not None:
                topics.append((current_topic, "\n".join(current_content_lines)))
            current_topic = topic_match.group(1).strip()
            current_content_lines = []
        elif current_topic is not None:
            current_content_lines.append(line)

    # Save last topic
    if current_topic is not None:
        topics.append((current_topic, "\n".join(current_content_lines)))

    # Filter to only discussion topics (exclude non-discussion ### headers)
    exclude_headers = [
        r"出席人員", r"請假人員", r"缺席人員",
        r"Present", r"On Leave", r"Absent",
        r"技術術語", r"商業術語", r"部門名稱",
        r"中文姓名", r"英文姓名", r"會議相關", r"動詞",
    ]
    discussion_topics = [
        (name, body) for name, body in topics
        if not any(re.search(pat, name) for pat in exclude_headers)
        and re.search(r"(討論重點|Key Discussion|決議|Decision|待辦|Action)", body, re.IGNORECASE)
    ]

    if len(discussion_topics) > 0:
        report.add(ValidationResult(
            Severity.PASS, Category.DISCUSSION,
            f"找到 {len(discussion_topics)} 個討論議題",
            f"Found {len(discussion_topics)} discussion topic(s)"
        ))

        for topic_name, topic_body in discussion_topics:
            has_discussion = bool(re.search(r"(討論重點|Key Discussion)", topic_body, re.IGNORECASE))
            has_decision = bool(re.search(r"(決議事項|Decision)", topic_body, re.IGNORECASE))
            has_action = bool(re.search(r"(待辦事項|Action Item)", topic_body, re.IGNORECASE))

            if not has_decision:
                report.add(ValidationResult(
                    Severity.WARNING, Category.DISCUSSION,
                    f"議題「{topic_name}」缺少決議事項",
                    f"Topic \"{topic_name}\" is missing decisions"
                ))
    else:
        report.add(ValidationResult(
            Severity.WARNING, Category.DISCUSSION,
            "未找到包含完整討論內容的議題區塊",
            "No discussion topic blocks with complete content found"
        ))


def validate_action_items(content: str, report: ValidationReport):
    """Check action items have required fields."""
    action_items_en = ACTION_ITEM_PATTERN_EN.findall(content)
    action_items_zh = ACTION_ITEM_PATTERN_ZH.findall(content)
    all_items = action_items_en + action_items_zh

    # Also find checkbox lines that might not fully match
    checkbox_lines = re.findall(r"- \[[ x]\]\s+(.+)", content)

    if len(checkbox_lines) == 0:
        report.add(ValidationResult(
            Severity.WARNING, Category.ACTION_ITEMS,
            "未找到任何待辦事項",
            "No action items found"
        ))
        return

    placeholder_items = [line for line in checkbox_lines if has_placeholder(line)]
    real_items = [line for line in checkbox_lines if not has_placeholder(line)]

    if len(real_items) == 0:
        report.add(ValidationResult(
            Severity.WARNING, Category.ACTION_ITEMS,
            "所有待辦事項皆為佔位符",
            "All action items are placeholders"
        ))
        return

    report.add(ValidationResult(
        Severity.PASS, Category.ACTION_ITEMS,
        f"找到 {len(real_items)} 項待辦事項",
        f"Found {len(real_items)} action item(s)"
    ))

    # Check each real action item for owner and due date
    for item_line in real_items:
        has_owner = bool(re.search(r"(負責人|Owner)\s*:\s*\S+", item_line))
        has_due = bool(re.search(r"(期限|Due)\s*:\s*\S+", item_line))

        if not has_owner:
            short_desc = item_line[:40] + ("..." if len(item_line) > 40 else "")
            report.add(ValidationResult(
                Severity.WARNING, Category.ACTION_ITEMS,
                f"待辦事項缺少負責人: 「{short_desc}」",
                f"Action item missing owner: \"{short_desc}\""
            ))

        if not has_due:
            short_desc = item_line[:40] + ("..." if len(item_line) > 40 else "")
            report.add(ValidationResult(
                Severity.WARNING, Category.ACTION_ITEMS,
                f"待辦事項缺少期限: 「{short_desc}」",
                f"Action item missing due date: \"{short_desc}\""
            ))


def validate_structure(content: str, report: ValidationReport):
    """Check required template sections exist."""
    for section_name, patterns in REQUIRED_SECTIONS.items():
        found = any(re.search(pat, content, re.IGNORECASE) for pat in patterns)
        section_labels = {
            "metadata": ("會議基本資訊區塊", "Meeting information section"),
            "participants": ("與會人員區塊", "Participants section"),
            "agenda": ("議程區塊", "Agenda section"),
            "discussion": ("討論內容區塊", "Discussion section"),
            "next_meeting": ("下次會議區塊", "Next meeting section"),
        }
        zh_label, en_label = section_labels[section_name]

        if found:
            report.add(ValidationResult(
                Severity.PASS, Category.STRUCTURE,
                f"{zh_label}存在", f"{en_label} exists"
            ))
        else:
            report.add(ValidationResult(
                Severity.ERROR, Category.STRUCTURE,
                f"缺少{zh_label}", f"Missing {en_label}"
            ))


def validate_cross_references(content: str, report: ValidationReport,
                              provided_participants: Optional[list[str]] = None):
    """Check that action item owners appear in participant list."""
    participants = extract_participants(content)
    owners = extract_action_item_owners(content)

    if not owners:
        return

    # Use provided participants as authoritative source if available,
    # otherwise fall back to participants extracted from the notes
    if provided_participants:
        participant_set = set(provided_participants)
    elif participants:
        participant_set = {p.strip() for p in participants}
    else:
        return

    for owner in owners:
        owner_clean = owner.strip()
        if owner_clean in participant_set:
            report.add(ValidationResult(
                Severity.PASS, Category.CROSS_REFERENCE,
                f"待辦負責人「{owner_clean}」已在與會人員名單中",
                f"Action item owner \"{owner_clean}\" is in participant list"
            ))
        else:
            report.add(ValidationResult(
                Severity.WARNING, Category.CROSS_REFERENCE,
                f"待辦負責人「{owner_clean}」未出現在與會人員名單中",
                f"Action item owner \"{owner_clean}\" is NOT in participant list"
            ))


# ---------------------------------------------------------------------------
# Glossary & Transcript Coverage
# ---------------------------------------------------------------------------

def load_glossary(glossary_path: str) -> dict[str, list[str]]:
    """Load glossary and build a correction map: {correct_term: [error_variants]}."""
    correction_map: dict[str, list[str]] = {}
    path = Path(glossary_path)
    if not path.exists():
        return correction_map

    content = path.read_text(encoding="utf-8")
    # Pattern: "- 正確詞 (說明) - 常見錯誤: 錯誤1、錯誤2"
    # or:      "- 正確詞 - 常見錯誤: 錯誤1、錯誤2"
    # or:      "- 正確詞 - Common errors: err1, err2"
    pattern = re.compile(
        r"^- (.+?)(?:\s*\(.+?\))?\s*-\s*(?:常見錯誤|Common errors?):\s*(.+)$",
        re.MULTILINE,
    )
    for match in pattern.finditer(content):
        correct_term = match.group(1).strip()
        errors_raw = match.group(2).strip()
        # Split by 、 or , or 、
        errors = [e.strip() for e in re.split(r"[、,，]", errors_raw) if e.strip()]
        correction_map[correct_term] = errors

    return correction_map


def apply_glossary_corrections(text: str, correction_map: dict[str, list[str]]) -> str:
    """Apply glossary corrections to raw transcript text."""
    corrected = text
    for correct_term, error_variants in correction_map.items():
        for error in error_variants:
            if error in corrected:
                corrected = corrected.replace(error, correct_term)
    return corrected


@dataclass
class KeyFact:
    """A key fact extracted from the transcript."""
    category: str       # "person", "number", "date", "decision", "action", "term"
    value: str          # The extracted value
    context: str        # Surrounding text for display
    search_terms: list[str]  # Terms to search for in meeting notes


def extract_key_facts(
    transcript: str,
    correction_map: dict[str, list[str]],
) -> list[KeyFact]:
    """Extract key facts from a corrected transcript."""
    facts: list[KeyFact] = []
    seen: set[str] = set()

    # --- 1. Person names (from glossary) ---
    glossary_names_section_terms = set()
    for term in correction_map:
        # Heuristic: Chinese names are 2-4 chars, English names contain spaces
        if (2 <= len(term) <= 4 and re.match(r"^[\u4e00-\u9fff]+$", term)) or \
           re.match(r"^[A-Z][a-z]+ [A-Z]", term):
            glossary_names_section_terms.add(term)

    for name in glossary_names_section_terms:
        if name in transcript and name not in seen:
            # Get context (up to 20 chars around the match)
            idx = transcript.index(name)
            start = max(0, idx - 15)
            end = min(len(transcript), idx + len(name) + 15)
            context = "..." + transcript[start:end] + "..."
            facts.append(KeyFact("person", name, context, [name]))
            seen.add(name)

    # --- 2. Numbers, percentages, monetary amounts ---
    number_patterns = [
        # Percentages: 80%, 百分之八十
        (r"\d+\.?\d*\s*%", "number"),
        (r"百分之[零一二三四五六七八九十百]+", "number"),
        # Monetary: $5M, 300萬, 5000元, NT\$..., USD...
        (r"(?:NT\$|USD?|\$)\s*[\d,.]+[KMBkmb]?", "number"),
        (r"\d+(?:\.\d+)?\s*[萬億千百](?:元|塊)?", "number"),
        (r"\d{1,3}(?:,\d{3})+(?:\.\d+)?\s*元?", "number"),
        # Large standalone numbers (5+ digits or with commas) — likely significant
        (r"\d{5,}", "number"),
        # Specific quantities: 3個月, 5人, 10天, 2週
        (r"\d+\s*(?:個月|個人|人|天|週|周|年|季|次|件|台|組|批|份|項)", "number"),
    ]
    for pat_str, cat in number_patterns:
        for match in re.finditer(pat_str, transcript):
            value = match.group().strip()
            if value not in seen and len(value) >= 2:
                idx = match.start()
                start = max(0, idx - 15)
                end = min(len(transcript), match.end() + 15)
                context = "..." + transcript[start:end] + "..."
                facts.append(KeyFact(cat, value, context, [value]))
                seen.add(value)

    # --- 3. Dates ---
    date_patterns = [
        r"\d{4}[-/]\d{1,2}[-/]\d{1,2}",
        r"\d{1,2}月\d{1,2}[日號]",
        r"(?:下|上|這)(?:週|周|禮拜)[一二三四五六日天]",
        r"(?:明|後|前|昨)天",
        r"(?:下|上|這)個月",
        r"Q[1-4]",
        r"第[一二三四]季",
    ]
    for pat_str in date_patterns:
        for match in re.finditer(pat_str, transcript):
            value = match.group().strip()
            if value not in seen:
                idx = match.start()
                start = max(0, idx - 15)
                end = min(len(transcript), match.end() + 15)
                context = "..." + transcript[start:end] + "..."
                facts.append(KeyFact("date", value, context, [value]))
                seen.add(value)

    # --- 4. Decision / conclusion sentences ---
    decision_markers = [
        r"決定", r"決議", r"同意", r"通過", r"否決", r"拍板", r"確認",
        r"結論是", r"最終方案", r"我們決定", r"大家同意",
        r"decided", r"agreed", r"approved", r"conclusion",
    ]
    for marker in decision_markers:
        for match in re.finditer(marker, transcript, re.IGNORECASE):
            idx = match.start()
            # Find the sentence containing this marker (bounded by newlines or sentence-end punctuation)
            line_start = transcript.rfind("\n", 0, idx)
            line_start = line_start + 1 if line_start != -1 else 0
            line_end = transcript.find("\n", idx)
            line_end = line_end if line_end != -1 else len(transcript)
            sentence = transcript[line_start:line_end].strip()
            # Clean up numbering prefixes like "1. " "2. "
            sentence_clean = re.sub(r"^\d+\.\s*", "", sentence).strip()
            # Skip pure header/label lines (e.g., "決定事項：")
            if re.match(r"^.{0,6}[：:]\s*$", sentence_clean):
                continue
            if sentence_clean not in seen and len(sentence_clean) >= 4:
                context = "..." + sentence + "..."
                # Search terms: the full sentence and core keywords within it
                search_terms = [sentence_clean]
                # Also add a shorter key phrase (first 20 chars) for fuzzy matching
                if len(sentence_clean) > 20:
                    search_terms.append(sentence_clean[:20])
                facts.append(KeyFact("decision", sentence_clean, context, search_terms))
                seen.add(sentence_clean)

    # --- 5. Action / assignment sentences ---
    action_markers = [
        r"負責", r"請.{1,6}(?:處理|完成|負責|準備|跟進|追蹤)",
        r"要在.{0,10}之前", r"截止日期", r"deadline",
        r"assigned to", r"responsible for", r"action item",
    ]
    for marker in action_markers:
        for match in re.finditer(marker, transcript, re.IGNORECASE):
            idx = match.start()
            # Extract the full line containing this marker
            line_start = transcript.rfind("\n", 0, idx)
            line_start = line_start + 1 if line_start != -1 else 0
            line_end = transcript.find("\n", idx)
            line_end = line_end if line_end != -1 else len(transcript)
            sentence = transcript[line_start:line_end].strip()
            sentence_clean = re.sub(r"^\d+\.\s*", "", sentence).strip()
            if sentence_clean not in seen and len(sentence_clean) >= 4:
                context = "..." + sentence + "..."
                search_terms = [sentence_clean]
                if len(sentence_clean) > 20:
                    search_terms.append(sentence_clean[:20])
                facts.append(KeyFact("action", sentence_clean, context, search_terms))
                seen.add(sentence_clean)

    # --- 6. Glossary technical/business terms mentioned ---
    non_name_terms = set(correction_map.keys()) - glossary_names_section_terms
    for term in non_name_terms:
        if term in transcript and term not in seen:
            idx = transcript.index(term)
            start = max(0, idx - 15)
            end = min(len(transcript), idx + len(term) + 15)
            context = "..." + transcript[start:end] + "..."
            facts.append(KeyFact("term", term, context, [term]))
            seen.add(term)

    return facts


def validate_transcript_coverage(
    transcript_path: str,
    notes_content: str,
    report: ValidationReport,
    glossary_path: Optional[str] = None,
):
    """Validate that key facts from the transcript appear in the meeting notes."""
    transcript_file = Path(transcript_path)
    if not transcript_file.exists():
        report.add(ValidationResult(
            Severity.ERROR, Category.TRANSCRIPT_COVERAGE,
            f"找不到逐字稿檔案: {transcript_path}",
            f"Transcript file not found: {transcript_path}",
        ))
        return

    raw_transcript = transcript_file.read_text(encoding="utf-8")

    # Load glossary if provided
    correction_map: dict[str, list[str]] = {}
    if glossary_path:
        correction_map = load_glossary(glossary_path)

    # Apply corrections to transcript
    corrected_transcript = apply_glossary_corrections(raw_transcript, correction_map)

    # Extract key facts
    facts = extract_key_facts(corrected_transcript, correction_map)

    if not facts:
        report.add(ValidationResult(
            Severity.WARNING, Category.TRANSCRIPT_COVERAGE,
            "未能從逐字稿中提取到關鍵事實（可能逐字稿內容過短或格式特殊）",
            "Could not extract key facts from transcript (content may be too short or in unusual format)",
        ))
        return

    # Category labels for display
    cat_labels_zh = {
        "person": "👤 人名", "number": "🔢 數字", "date": "📅 日期",
        "decision": "🔨 決策", "action": "📌 行動", "term": "📖 術語",
    }
    cat_labels_en = {
        "person": "👤 Person", "number": "🔢 Number", "date": "📅 Date",
        "decision": "🔨 Decision", "action": "📌 Action", "term": "📖 Term",
    }

    found_count = 0
    missing_facts: list[KeyFact] = []

    def normalize(text: str) -> str:
        """Remove whitespace and common punctuation differences for fuzzy matching."""
        return re.sub(r"[\s\u3000\u00a0]+", "", text).lower()

    notes_normalized = normalize(notes_content)

    for fact in facts:
        # Check if any of the search terms appear in the meeting notes
        # Try both exact match and normalized (whitespace-insensitive) match
        is_found = any(term in notes_content for term in fact.search_terms)
        if not is_found:
            is_found = any(normalize(term) in notes_normalized for term in fact.search_terms)
        if is_found:
            found_count += 1
        else:
            missing_facts.append(fact)

    total = len(facts)
    coverage_pct = (found_count / total * 100) if total > 0 else 0

    # Overall coverage report
    if coverage_pct >= 80:
        report.add(ValidationResult(
            Severity.PASS, Category.TRANSCRIPT_COVERAGE,
            f"逐字稿覆蓋率: {coverage_pct:.0f}% ({found_count}/{total} 項關鍵事實已記錄)",
            f"Transcript coverage: {coverage_pct:.0f}% ({found_count}/{total} key facts recorded)",
        ))
    elif coverage_pct >= 50:
        report.add(ValidationResult(
            Severity.WARNING, Category.TRANSCRIPT_COVERAGE,
            f"逐字稿覆蓋率偏低: {coverage_pct:.0f}% ({found_count}/{total} 項關鍵事實已記錄)",
            f"Low transcript coverage: {coverage_pct:.0f}% ({found_count}/{total} key facts recorded)",
        ))
    else:
        report.add(ValidationResult(
            Severity.ERROR, Category.TRANSCRIPT_COVERAGE,
            f"逐字稿覆蓋率不足: {coverage_pct:.0f}% ({found_count}/{total} 項關鍵事實已記錄)",
            f"Insufficient transcript coverage: {coverage_pct:.0f}% ({found_count}/{total} key facts recorded)",
        ))

    # Report each missing fact
    for fact in missing_facts:
        zh_cat = cat_labels_zh.get(fact.category, fact.category)
        en_cat = cat_labels_en.get(fact.category, fact.category)
        report.add(ValidationResult(
            Severity.WARNING, Category.TRANSCRIPT_COVERAGE,
            f"未記錄 {zh_cat}「{fact.value}」— 出處: {fact.context}",
            f"Missing {en_cat} \"{fact.value}\" — source: {fact.context}",
        ))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def validate(file_path: str, transcript_path: Optional[str] = None,
             glossary_path: Optional[str] = None,
             participants: Optional[list[str]] = None) -> ValidationReport:
    """Run all validations on a meeting notes file."""
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")

    report = ValidationReport(file_path=str(path.name))

    validate_metadata(content, report)
    validate_participants(content, report, provided_participants=participants)
    validate_agenda(content, report)
    validate_discussion(content, report)
    validate_action_items(content, report)
    validate_structure(content, report)
    validate_cross_references(content, report, provided_participants=participants)

    # Transcript coverage validation (optional)
    if transcript_path:
        validate_transcript_coverage(transcript_path, content, report, glossary_path)

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Validate meeting notes markdown files"
    )
    parser.add_argument(
        "file",
        help="Path to the meeting notes markdown file to validate",
    )
    parser.add_argument(
        "--transcript",
        default=None,
        help="Path to the original transcript file for coverage validation",
    )
    parser.add_argument(
        "--glossary",
        default=None,
        help="Path to the glossary file for term correction (used with --transcript)",
    )
    parser.add_argument(
        "--participants",
        default=None,
        help="User-provided participant list: a file path (one name per line) "
             "or comma-separated names (e.g. '王小明,李小華,陳大同')",
    )
    parser.add_argument(
        "--lang",
        choices=["zh_TW", "en"],
        default=None,
        help="Output language (auto-detected if not specified)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output results as JSON",
    )

    args = parser.parse_args()
    file_path = Path(args.file)

    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Load user-provided participants
    provided_participants = None
    if args.participants:
        provided_participants = load_provided_participants(args.participants)
        if provided_participants:
            print(f"📋 Using provided participant list: {', '.join(provided_participants)}")
        else:
            print("⚠️  --participants provided but no names could be parsed.", file=sys.stderr)

    report = validate(str(file_path), args.transcript, args.glossary, provided_participants)

    if args.output_json:
        print(report.to_json())
    else:
        lang = args.lang or detect_language(file_path.read_text(encoding="utf-8"))
        print(report.display(lang))

    # Exit code: 1 if any errors, 0 otherwise
    sys.exit(1 if report.error_count > 0 else 0)


if __name__ == "__main__":
    main()
