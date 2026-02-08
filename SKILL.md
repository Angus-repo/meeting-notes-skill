---
name: meeting-notes
description: Professional meeting minutes creation and transcription processing for enterprise use. Use when creating meeting notes, processing meeting transcripts, converting speech-to-text output into structured minutes, correcting transcription errors, or organizing meeting documentation. Applies terminology correction, participant identification, and standardized formatting to produce consistent meeting records.
---

# Meeting Notes

## Overview

This skill transforms meeting transcripts and raw content into professional, structured meeting minutes following enterprise standards. It includes automatic error correction using a customizable glossary, participant verification, and template-based formatting.

## Workflow

### Step 1: Review the Glossary

Before processing any meeting content, read the terminology glossary to understand correction patterns:

```
references/glossary.md
```

The glossary contains:
- Technical terminology and common transcription errors
- Business terms and acronyms
- Department names
- Person names
- Company/product names

**Note**: The glossary is user-editable. Users can update it at any time to improve correction accuracy.

### Step 2: Process and Correct Transcript

When receiving meeting content (transcript, text, speech-to-text output):

1. **Apply corrections** using the glossary:
   - Match common transcription errors to correct terms
   - Fix terminology, acronyms, and proper nouns
   - Preserve the original meaning while correcting mistakes

2. **Document all corrections** in a clear list:
   ```
   ## 文字校正記錄
   
   以下是根據詞彙表進行的校正：
   
   - "欸愛" → "AI"
   - "開批愛" → "KPI"
   - "王曉明" → "王小明"
   [... more corrections ...]
   ```

3. **Present the corrected text** to the user for review before proceeding

### Step 3: Identify and Verify Participants

Extract person names from the corrected transcript:

1. **List all identified participants** and ask the user to verify:
   ```
   ## 請確認與會人員
   
   我從會議內容中識別出以下人員，請確認是否正確：
   
   - 王小明
   - 李小華
   - 陳大同
   
   請問：
   1. 以上名單是否正確？
   2. 是否有遺漏的與會人員？
   3. 是否需要補充職稱/部門資訊？
   ```

2. **Wait for user confirmation** before generating the final meeting notes

### Step 4: Generate Meeting Notes

Using the meeting template, create structured meeting minutes:

1. **Load the template**:
   ```
   assets/meeting-template.md
   ```

2. **Fill in all sections** with information from the corrected transcript:
   - Meeting basic information (date, time, location, chair, recorder)
   - Participant list (categorized as present/on-leave/absent)
   - Agenda items
   - Discussion summaries by topic
   - Decisions and action items
   - Next meeting arrangements

3. **Ensure all action items** include:
   - Clear task description
   - Responsible person
   - Due date
   - Checkbox for tracking

4. **Output the complete meeting notes** in markdown format following the template structure

## Template

The meeting notes template provides a standardized structure for all meeting records:

```
assets/meeting-template.md
```

The template includes sections for:
- Meeting basic information (name, date, time, location, chair, recorder)
- Participant lists (present, on leave, absent)
- Agenda items
- Discussion summaries with decisions and action items
- Next meeting arrangements
- Attachments and notes

## Glossary

The terminology glossary is a user-editable reference for correction patterns:

```
references/glossary.md
```

Users should update this file regularly to:
- Add new technical terms and acronyms
- Include new team members' names
- Add product/project names
- Record common transcription errors specific to their domain

## Usage Examples

**Example 1: Basic transcript processing**

User: "請幫我處理這個會議逐字稿：今天開批愛檢討會議，王曉明報告了欸愛專案的進度..."

Claude:
1. Reads glossary.md
2. Corrects errors: "開批愛" → "KPI", "王曉明" → "王小明", "欸愛" → "AI"
3. Shows correction list to user
4. Identifies participant: 王小明
5. Asks user to verify participants and provide additional meeting details
6. Generates meeting notes using the template

**Example 2: Update glossary**

User: "請更新詞彙表，新增我們的產品名稱 CloudSync，常被辨識為 Cloud Sink"

Claude: Updates references/glossary.md with the new entry

## Best Practices

1. **Always review glossary first** - Understanding correction patterns improves accuracy
2. **Show corrections transparently** - Users should see what was changed and why
3. **Verify participants** - Don't assume participant lists are complete
4. **Use the template consistently** - Maintains professional standards across all meeting notes
5. **Encourage glossary updates** - Better glossary = better corrections over time

