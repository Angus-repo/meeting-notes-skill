# 📝 Meeting Notes Skill

**English** | [繁體中文](README_zh_TW.md)

A GitHub Copilot custom skill for transforming meeting transcripts into professional, structured meeting minutes with automatic transcription error correction.

## Overview

**Meeting Notes** skill helps you convert raw meeting transcripts (especially speech-to-text output) into well-organized meeting minutes. It leverages a customizable glossary to automatically correct common transcription errors in terminology, names, and acronyms, then formats everything using a standardized template.

## ✨ Features

- **🔤 Automatic Transcription Correction** — Fixes common speech-to-text errors using a user-editable glossary (e.g., "欸愛" → "AI", "開批愛" → "KPI")
- **👥 Participant Identification & Verification** — Extracts attendee names from transcripts and confirms with the user before finalizing
- **📋 Standardized Template Formatting** — Generates consistent, professional meeting minutes with structured sections
- **🌐 Multilingual Templates** — Supports both English and Traditional Chinese (zh_TW) meeting templates
- **📖 Editable Glossary** — Users can continuously update the terminology glossary to improve correction accuracy over time
- **🧠 Glossary Auto-Learning** — Automatically suggests adding new correction patterns discovered during transcript processing to the glossary
- **✅ Meeting Notes Validator** — Python script that validates meeting notes for completeness, formatting, and cross-reference consistency

## 📁 Project Structure

```
meeting-notes/
├── meeting-notes.skill    # Skill manifest
├── SKILL.md               # Skill instructions for Copilot
├── README.md              # This file (English)
├── README_zh_TW.md        # README (繁體中文)
├── assets/
│   ├── meeting-template.md          # Meeting template (English)
│   └── meeting-template_zh_TW.md    # Meeting template (繁體中文)
├── references/
│   ├── glossary.md        # Terminology glossary (English)
│   └── glossary_zh_TW.md  # Terminology glossary (繁體中文)
└── scripts/
    └── validate_notes.py  # Meeting notes validation script
```

## 🚀 Getting Started

### Prerequisites

- [GitHub Copilot](https://github.com/features/copilot) with custom skills support
- VS Code or a compatible editor

### Installation

1. Clone this repository or copy the skill folder into your Copilot skills directory:
   ```bash
   git clone https://github.com/Angus-repo/meeting-notes-skill.git
   ```

2. Customize the glossary at `references/glossary.md` with your team's:
   - Team member names
   - Company/product names
   - Domain-specific terminology
   - Common transcription errors

3. The skill is ready to use with GitHub Copilot!

## 📖 Usage

### Basic Transcript Processing

Provide a raw meeting transcript to Copilot and ask it to generate meeting notes:

```
請幫我處理這個會議逐字稿：
今天開批愛檢討會議，王曉明報告了欸愛專案的進度...
```

The skill will:

1. **Read the glossary** to understand correction patterns
2. **Correct transcription errors** and present a correction log
3. **Identify participants** and ask you to verify
4. **Generate structured meeting minutes** using the template

### Update the Glossary

You can ask Copilot to update the glossary with new terms:

```
請更新詞彙表，新增我們的產品名稱 CloudSync，常被辨識為 Cloud Sink
```

## 📄 Templates

| Template | Language | File |
|----------|----------|------|
| English | EN | `assets/meeting-template.md` |
| 繁體中文 | zh_TW | `assets/meeting-template_zh_TW.md` |

Both templates include sections for:
- Meeting basic information (title, date, time, location, chair, recorder)
- Attendee lists (present / on leave / absent)
- Agenda items
- Discussion summaries with decisions and action items
- Next meeting arrangements
- Attachments and notes

## ✅ Validation

Use the built-in validation script to check your meeting notes for completeness and correctness:

```bash
# Validate with auto-detected language
python3 scripts/validate_notes.py path/to/meeting-notes.md

# Specify output language
python3 scripts/validate_notes.py path/to/meeting-notes.md --lang zh_TW

# Output as JSON (for automation)
python3 scripts/validate_notes.py path/to/meeting-notes.md --json

# Validate with transcript coverage check
python3 scripts/validate_notes.py path/to/meeting-notes.md \
  --transcript path/to/transcript.txt \
  --glossary references/glossary_zh_TW.md
```

The validator checks:

| Check | Description |
|-------|-------------|
| Metadata completeness | All fields (date, time, location, chair, recorder) are filled in |
| Date format | Dates follow YYYY-MM-DD format |
| Participants | At least one attendee is listed |
| Agenda items | At least one real agenda item exists |
| Discussion sections | Topics have discussion points and decisions |
| Action item format | Each action item has owner and due date |
| Template structure | All required sections are present |
| Cross-reference | Action item owners appear in participant list |
| **Transcript coverage** | Key facts from the transcript are recorded in the notes |

### Transcript Coverage Validation

When `--transcript` is provided, the validator extracts **key facts** from the original transcript and checks if they appear in the meeting notes:

| Fact Type | What It Extracts |
|-----------|------------------|
| 👤 Person | Names from the glossary found in the transcript |
| 🔢 Number | Percentages, monetary amounts, quantities |
| 📅 Date | Dates, deadlines, time references |
| 🔨 Decision | Sentences containing decision keywords (決定/同意/agreed/approved) |
| 📌 Action | Sentences with assignment keywords (負責/截止/assigned to) |
| 📖 Term | Technical and business terms from the glossary |

Coverage thresholds:
- ≥ 80% → ✅ Pass
- 50–79% → ⚠️ Warning
- < 50% → ❌ Error

## 🔧 Customization

### Glossary (`references/glossary.md`)

The glossary supports the following categories:

| Category | Examples |
|----------|----------|
| Technical Terms | AI, API, CI/CD, DevOps, Kubernetes |
| Business Terms | KPI, ROI, SOP, OKR, B2B |
| Department Names | 研發部, 業務部, 行銷部 |
| Person Names | Chinese & English names |
| Company/Product Names | Custom entries |
| Meeting-specific Vocabulary | 議程, 決議, 共識 |

> **Tip:** Regularly update the glossary when new team members join, new projects start, or new transcription errors are discovered.

## 💡 Best Practices

1. **Keep the glossary up to date** — Better glossary = better correction accuracy
2. **Always verify corrections** — Review the correction log before finalizing
3. **Confirm participant lists** — Don't assume the auto-detected list is complete
4. **Use templates consistently** — Maintains professional standards across all meeting records
5. **Add domain-specific terms** — Industry jargon and internal terms improve results significantly

## 📜 License

This project is open source. Feel free to use and modify it for your team's needs.

## 🤝 Contributing

Contributions are welcome! You can help by:
- Adding new templates for different meeting types
- Expanding the glossary with more terminology
- Adding automation scripts
- Improving documentation

---

Made with ❤️ for better meeting documentation.
