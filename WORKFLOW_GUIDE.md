# Telegram Study Bot (n8n + Gemini) — English Production Guide

This repo includes an importable workflow file for n8n:
- `telegram-study-bot-workflow.json`

> Security note: do **not** hardcode real API keys/tokens in workflow JSON. Configure them in n8n credentials or environment variables.

## Quick start (n8n)

1. Import `telegram-study-bot-workflow.json` into n8n.
2. Set environment variables (or replace with n8n credentials expressions):
   - `TELEGRAM_BOT_TOKEN`
   - `GEMINI_API_KEY`
   - `ADMIN_USER_ID` (optional, for admin notifications)
3. Activate the workflow.
4. Send either:
   - PDF document (supported type: `application/pdf`)
   - plain text message / caption

## Workflow overview (node-by-node)

1. **Telegram Trigger**: receives incoming Telegram `message` updates.
2. **Normalize Input**: extracts `chat_id`, `user_id`, `file_id`, `file_name`, `mime_type`, `text_or_caption`.
3. **Send Processing Message (AR)**: sends immediate Arabic “processing” UX message.
4. **IF Has Document?**:
   - yes → document pipeline
   - no → text pipeline
5. **IF PDF Mime Type?**: validates incoming document is PDF.
6. **Send Unsupported Type Error (AR)**: Arabic fallback for unsupported file type.
7. **Telegram Get File**: fetches Telegram `file_path` using `file_id`.
8. **Download PDF Binary**: downloads binary from Telegram file endpoint.
9. **Extract Text from PDF**: extracts text from binary PDF.
10. **Clean Text**: cleans spaces/newlines for both PDF text and direct text.
11. **IF Empty Text?**: sends Arabic fallback if text is empty.
12. **Chunk Text**: chunking for long lectures.
13. **Gemini Chunk Summary**: summarizes each chunk with low temperature.
14. **Merge Chunk Summaries**: merges partial summaries in order.
15. **Gemini Final Summary**: builds final structured Arabic summary.
16. **Gemini Generate MCQs**: generates 10 MCQs + answers/explanations.
17. **Build Final Text Blocks**: extracts summary/high-yield/questions/answers blocks.
18. **IF AI Failed?**: handles Gemini/API empty/failure outputs.
19. **Split For Telegram**: splits long messages under Telegram length constraints.
20. **Telegram Send Result**: sends ordered output blocks.
21. **Send Telegram Failure Fallback (AR)**: Arabic fallback on delivery issues.

## Exact n8n nodes used

- `n8n-nodes-base.telegramTrigger`
- `n8n-nodes-base.telegram`
- `n8n-nodes-base.if`
- `n8n-nodes-base.httpRequest`
- `n8n-nodes-base.extractFromFile`
- `n8n-nodes-base.code`

## Gemini prompt (Final Summary node)

```text
Transform the intermediate chunk summaries into one final, professional Arabic study summary.
Rules:
- Do not add any information not present in the lecture content.
- Keep medical/scientific terms in English exactly as written.
- Be concise, high-yield, exam-oriented.
- Use this exact structure:
  - Lecture Title / Topic
  - Short Overview
  - High-Yield Points
  - Important Definitions
  - Key Lists / Classifications / Mechanisms if present
  - Common Exam Traps
  - Quick Revision

Intermediate summaries:
{{$json.merged_chunk_summaries}}
```

Recommended generation config:
- temperature: `0.2`
- maxOutputTokens: `2200`

## Gemini prompt (MCQ node)

```text
Using ONLY the lecture content below, generate exactly 10 university-level MCQs.
Hard constraints:
1) Each question has 4 options: A, B, C, D.
2) No external facts beyond the lecture text.
3) Vary difficulty (easy / medium / hard).
4) After all questions, add a section titled: Answers & Explanations.
5) For each question provide: correct answer + short explanation.
6) Write in Arabic, while preserving medical/scientific terms in English as-is.

Lecture text:
{{$json.source_text}}
```

Recommended generation config:
- temperature: `0.3`
- maxOutputTokens: `2600`

## Code snippets

### 1) Clean text

```javascript
const lectureText = $json.text || '';
const inputText = $json.text_or_caption || '';
const sourceText = (lectureText || inputText || '').trim();

if (!sourceText) {
  return [{ json: { ...$json, source_text: '', is_empty: true } }];
}

const cleaned = sourceText
  .replace(/\r/g, '\n')
  .replace(/\t+/g, ' ')
  .replace(/[ ]{2,}/g, ' ')
  .replace(/\n{3,}/g, '\n\n')
  .trim();

return [{ json: { ...$json, source_text: cleaned, is_empty: cleaned.length === 0 } }];
```

### 2) Chunk long text

```javascript
const text = $json.source_text || '';
const MAX_CHARS = 12000;
const OVERLAP = 500;

if (text.length <= MAX_CHARS) {
  return [{ json: { ...$json, chunk_index: 1, total_chunks: 1, chunk_text: text } }];
}

const chunks = [];
let start = 0;
while (start < text.length) {
  let end = Math.min(start + MAX_CHARS, text.length);
  if (end < text.length) {
    const boundary = text.lastIndexOf('\n', end);
    if (boundary > start + 3000) end = boundary;
  }
  chunks.push(text.slice(start, end).trim());
  if (end >= text.length) break;
  start = Math.max(0, end - OVERLAP);
}

return chunks.map((chunk, i) => ({
  json: {
    ...$json,
    chunk_index: i + 1,
    total_chunks: chunks.length,
    chunk_text: chunk,
  },
}));
```

### 3) Split long Telegram replies

```javascript
const TELEGRAM_LIMIT = 3900;

function splitLong(label, content) {
  const text = `${label}\n\n${content || ''}`.trim();
  if (text.length <= TELEGRAM_LIMIT) return [text];

  const parts = [];
  let rest = text;

  while (rest.length > TELEGRAM_LIMIT) {
    let cut = rest.lastIndexOf('\n', TELEGRAM_LIMIT);
    if (cut < 1000) cut = TELEGRAM_LIMIT;
    parts.push(rest.slice(0, cut).trim());
    rest = rest.slice(cut).trim();
  }

  if (rest) parts.push(rest);
  return parts;
}

const sections = [
  ['📘 Summary', $json.final_summary],
  ['🎯 High-Yield Points', $json.high_yield],
  ['❓ MCQs', $json.mcq_questions],
  ['✅ Answers with Explanations', $json.mcq_answers],
];

const out = [];
for (const [label, content] of sections) {
  for (const msg of splitLong(label, content)) {
    out.push({ json: { chat_id: $json.chat_id, text: msg } });
  }
}

return out;
```
