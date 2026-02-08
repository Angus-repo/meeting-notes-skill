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

3. **Identify new corrections not in the glossary**: Track any manual corrections or new patterns discovered during processing that are NOT already in the glossary. These will be suggested for glossary update in Step 2b.

4. **Present the corrected text** to the user for review before proceeding

### Step 2b: Glossary Auto-Learning Suggestion

After the user reviews and confirms the corrections, check if any corrections were made that are **not yet recorded** in the glossary. If so:

1. **Compile a list of new correction patterns** discovered during processing:
   ```
   ## 📚 詞彙表更新建議
   
   以下校正尚未收錄在詞彙表中，建議新增以提升未來校正準確度：
   
   | 正確詞彙 | 語音辨識錯誤 | 建議分類 |
   |----------|-------------|---------|
   | CloudSync | Cloud Sink、克勞新客 | 產品/專案名稱 |
   | 林志偉 | 林至偉、林之偉 | 常見人名 |
   
   是否要將以上項目新增至詞彙表？(全部新增 / 選擇性新增 / 略過)
   ```

2. **Wait for user confirmation**, then update the appropriate glossary file:
   - For Traditional Chinese context: `references/glossary_zh_TW.md`
   - For English context: `references/glossary.md`
   - Append new entries under the correct category section
   - Include the correct term, common errors, and category

3. **If the user also made manual corrections** to the presented text (corrections that the skill did not catch automatically), treat those as high-priority glossary candidates and highlight them:
   ```
   ⚠️ 您手動修正了以下內容，強烈建議加入詞彙表：
   - "賽佛" → "Server" (技術術語)
   ```

This ensures the glossary continuously improves with real-world usage data.

### Step 3: Confirm Participants

Since speech-to-text transcription often produces incorrect person names, **always ask the user to provide the participant list directly** rather than relying solely on transcript extraction.

1. **Proactively ask the user to provide the attendee list**:
   ```
   ## 請提供與會人員名單
   
   由於語音辨識對人名容易產生錯誤，請直接提供本次會議的出席人員名單：
   
   請提供以下資訊：
   1. 出席人員名單（可用逗號分隔，例如：王小明, 李小華, 陳大同）
   2. 請假人員（如有）
   3. 缺席人員（如有）
   4. 是否需要補充職稱/部門資訊？
   ```

2. **If the user provides names**, use them as the **authoritative attendee list**:
   - Save the list for use in Step 4 (filling meeting notes) and Step 5 (validation with `--participants`)
   - Cross-check against any names detected in the transcript and flag discrepancies
   - If transcript mentions someone not in the user's list, ask for clarification:
     ```
     逐字稿中提到「張大華」但未在您提供的名單中，請問是否需要加入？
     ```

3. **If the user prefers automatic extraction**, fall back to extracting from the transcript:
   - List all identified participants and ask the user to verify
   - Apply glossary corrections to fix common name errors
   - Present the list for confirmation before proceeding

4. **Wait for user confirmation** before generating the final meeting notes

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

### Step 5: Validate Meeting Notes

After generating the meeting notes, run the validation script to check for completeness and correctness:

```
scripts/validate_notes.py
```

1. **Run the validator** against the generated meeting notes:
   ```
   python scripts/validate_notes.py <meeting-notes-file.md>
   ```

2. **If the user provided a participant list**, include it for attendee verification:
   ```
   python scripts/validate_notes.py <meeting-notes-file.md> --participants '王小明,李小華,陳大同'
   ```
   Or if saved to a file (one name per line):
   ```
   python scripts/validate_notes.py <meeting-notes-file.md> --participants attendees.txt
   ```
   This will additionally check:
   - All specified participants appear in the meeting notes’ attendee section
   - No unrecognized names appear in the notes (possible transcript errors)
   - Action item owners match the provided participant list

3. **If the original transcript is available**, run with transcript coverage validation:
   ```
   python scripts/validate_notes.py <meeting-notes-file.md> --transcript <transcript.txt> --glossary references/glossary_zh_TW.md --participants '王小明,李小華,陳大同'
   ```
   This will additionally extract key facts (person names, numbers, dates, decisions, action items, technical terms) from the transcript and verify they appear in the meeting notes.

3. **Review the validation report** which checks:
   - **Metadata completeness**: All required fields (date, time, location, chair, recorder) are filled in and not placeholder text
   - **Date format correctness**: Dates follow YYYY-MM-DD format
   - **Participant section**: At least one participant is listed in the present section
   - **Agenda items**: At least one agenda item exists
   - **Discussion sections**: Each topic has discussion points, decisions, or action items
   - **Action item format**: Each action item has a description, responsible person, and due date
   - **Template structure**: All required sections from the template are present
   - **Cross-reference check**: All persons mentioned in action items appear in the participant list
   - **Transcript coverage** (when `--transcript` is provided): Key facts from the transcript are recorded in the meeting notes

3. **Address any warnings or errors** reported by the validator:
   ```
   ## 驗證結果
   
   ✅ 通過: 會議基本資訊完整
   ✅ 通過: 日期格式正確
   ⚠️ 警告: 待辦事項中的「張大華」未出現在與會人員名單中
   ⚠️ 警告: 未記錄 🔢 數字「300萬」
   ⚠️ 警告: 未記錄 📖 術語「ROI」
   ❌ 錯誤: 議題二缺少決議事項
   
   總計: 8 項通過, 3 項警告, 1 項錯誤
   ```

4. **Self-Correction Loop (Auto-Fix & Re-Validate)**

   When the validation report contains **errors (❌)** or **warnings (⚠️)**, you MUST automatically perform the following correction loop **without waiting for user input**:

   **Loop Start:**

   a. **Analyze each failed item** — Read the validation report and categorize each issue:
      - **Metadata issues**: Fill in missing fields (date, time, location, chair, recorder) from the transcript
      - **Missing participants**: Add persons mentioned in transcript to the participant list
      - **Missing agenda items**: Extract agenda topics from the transcript discussion flow
      - **Incomplete discussion sections**: Add missing 討論重點/決議/待辦 subsections with content from the transcript
      - **Action item format errors**: Ensure each action item has description, responsible person (`負責人`), and due date (`完成日期`)
      - **Cross-reference mismatches**: Add missing persons to the participant list, or correct name typos in action items
      - **Transcript coverage gaps**: For missing numbers, dates, decisions, terms, or action items flagged by the validator, locate the relevant content in the transcript and incorporate it into the appropriate section of the meeting notes

   b. **Apply corrections** to the meeting notes file — Edit the generated meeting notes directly to fix all identified issues

   c. **Re-run the validator** with the same command and arguments used in the initial validation

   d. **Check results**:
      - If **0 errors and 0 warnings** → Validation passed ✅, exit the loop and proceed to present the final notes to the user
      - If **0 errors but warnings remain** → Attempt to fix warnings. If a warning cannot be resolved (e.g., a number mentioned in the transcript is genuinely not relevant to the meeting notes), accept it and exit the loop
      - If **errors still remain** → Return to step (a) and repeat

   **Loop End** — Maximum 3 iterations to prevent infinite loops.

   e. **Report the correction summary** to the user after exiting the loop:
      ```
      ## 🔄 自動修正報告
      
      驗證腳本發現以下問題並已自動修正：
      
      | # | 問題類型 | 原始問題 | 修正方式 |
      |---|---------|---------|---------|
      | 1 | ❌ 錯誤 | 議題二缺少決議事項 | 從逐字稿補充決議內容 |
      | 2 | ⚠️ 警告 | 未記錄數字「300萬」 | 補充至預算討論段落 |
      | 3 | ⚠️ 警告 | 未記錄術語「ROI」 | 補充至成效分析段落 |
      
      修正後驗證結果: ✅ 全部通過 (18 項通過, 0 項警告, 0 項錯誤)
      ```

   f. If any issues **could not be auto-fixed**, clearly flag them for the user:
      ```
      ⚠️ 以下項目無法自動修正，請人工確認：
      - 待辦事項中的「張大華」未出現在與會人員名單中 — 此人名未在逐字稿中出現，請確認是否正確
      ```

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

**Example 2: Full workflow with validation and auto-correction**

User: "請幫我處理這份逐字稿，生成會議紀錄" (attaches transcript file)

Claude:
1. Reads glossary → corrects transcript → shows corrections to user
2. User confirms corrections → auto-learning suggests new glossary entries
3. **Asks user to provide attendee list** → user says: "出席: 王小明, 李小華, 陳大同"
4. Generates meeting notes using the template → saves to file
5. Runs validator: `python scripts/validate_notes.py meeting-notes.md --transcript transcript.txt --glossary references/glossary_zh_TW.md --participants '王小明,李小華,陳大同'`
6. Validator reports: 2 warnings (missing number "300萬", missing term "ROI")
7. **Auto-fix iteration 1**: Locates "300萬" and "ROI" in transcript, adds them to relevant discussion sections
8. Re-runs validator → 0 errors, 0 warnings ✅
9. Presents final meeting notes + auto-correction report to user

**Example 3: Update glossary**

User: "請更新詞彙表，新增我們的產品名稱 CloudSync，常被辨識為 Cloud Sink"

Claude: Updates references/glossary.md with the new entry

## Best Practices

1. **Always review glossary first** - Understanding correction patterns improves accuracy
2. **Show corrections transparently** - Users should see what was changed and why
3. **Verify participants** - Don't assume participant lists are complete
4. **Use the template consistently** - Maintains professional standards across all meeting notes
5. **Encourage glossary updates** - Better glossary = better corrections over time
6. **Accept glossary auto-learning suggestions** - Continuously improving the glossary with real corrections leads to better results
7. **Always validate before finalizing** - Run the validation script to catch missing fields, formatting issues, and cross-reference errors. **Never** present meeting notes to the user without passing validation first
8. **Auto-fix until clean** - When validation reports errors or warnings, automatically correct the meeting notes and re-validate in a loop (max 3 iterations). Only present the final notes to the user after validation passes or all fixable issues are resolved

