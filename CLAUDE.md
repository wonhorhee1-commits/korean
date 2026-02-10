# Korean Coach — Development Guide

## Project Overview
Korean learning tool for an intermediate/advanced speaker targeting full fluency. Two interfaces:
- **Web app** (`docs/index.html`) — GitHub Pages, the primary interface
- **CLI** (`python main.py`) — Rich-based terminal UI, secondary

## Architecture
- `docs/index.html` — Single-file web app (HTML/CSS/JS, no build step)
- `docs/data/*.json` — Data served by GitHub Pages
- `data/*.json` — Source of truth for all data
- `data/batch_*.json` — Intermediate batch files from expansion runs
- `data/enriched_*.json` — Intermediate enrichment files (notes added to entries)
- `merge_data.py` — Merges batch files into main data, syncs to `docs/data/`
- SM-2 spaced repetition algorithm (same as Anki)
- Firebase anonymous auth + Firestore for cross-device sync (config in index.html)

## Data Files

### Core Data
| File | Description | Count |
|---|---|---|
| `data/vocab.json` | Vocabulary entries by category | 5005 entries, 104 categories |
| `data/grammar.json` | Grammar patterns by category | 101 patterns, 8 categories |

### Fluency Drill Data
| File | Description | Count |
|---|---|---|
| `data/error_drills.json` | Error correction drills (find & fix grammar mistakes) | 60 drills |
| `data/grammar_context.json` | Grammar in context (pick correct pattern for paragraph) | 50 drills |
| `data/reading_drills.json` | Reading comprehension (passages + questions) | 30 passages |
| `data/register_drills.json` | Register switching (반말/해요체/격식체 conversion) | 40 drills |

### Vocab Categories & Required Fields
| Category | Fields |
|---|---|
| 한자어 (Sino-Korean) | korean, english, hanja, breakdown, example, example_en, notes |
| 뉘앙스 & 유의어 | korean (must contain " vs "), english, example, example_en, notes |
| 격식 & 문어체 | korean, english, example, example_en, notes |
| 사자성어 (Four-Character Idioms) | korean (EXACTLY 4 syllables), english, hanja (EXACTLY 4 chars), breakdown, example, example_en, notes |
| 관용어 (Korean Idioms) | korean, english, example, example_en, notes |
| Topic categories (주제별 단어) | korean, english, example, example_en, notes |

### Grammar Format
Each pattern: pattern, meaning, explanation, examples (array of {korean, english}), drill ({prompt, answer, full_sentence})

### Error Drill Format
Each drill: incorrect, correct, error_type, explanation

### Grammar Context Format
Each drill: passage (with _____ blank), options (4 choices), correct (index), explanation, category

### Reading Drill Format
Each drill: passage, passage_en, questions (array of {question, options, correct, explanation})

### Register Drill Format
Each drill: given, given_register, target_register, correct, explanation, difficulty, focus

## Web App Features (Menu Items)
1. **Vocabulary Drill** — Flashcard review with SRS, Korean↔English, self-rated
2. **Grammar Practice** — Pattern review + fill-in-the-blank drills
3. **Mixed Review** — Weakest cards first across all categories
4. **Sentence Production** — Given English sentence, construct Korean, compare to model
5. **Error Correction** — Find and fix subtle grammar mistakes in Korean sentences
6. **Grammar in Context** — Pick correct grammar pattern for a paragraph (4 options)
7. **Reading Comprehension** — Korean passages with multiple-choice questions
8. **Register Switching** — Convert between 반말/해요체/격식체
9. **View Progress** — SRS stats, weakest cards, accuracy

## Adding More Vocabulary (Batching Strategy)

### Workflow
1. Run parallel agents (one per category) to generate batch files: `data/batch_<name>.json`
2. Each agent reads existing `data/vocab.json` first to avoid duplicates
3. Merge with: `python merge_data.py` or manual Python merge script
4. Always sync to `docs/data/` after merging
5. Commit and push, user merges PR, GitHub Pages auto-updates

### Agent Prompts (copy-paste ready)
- **Light categories** (관용어, 뉘앙스, 격식): 4 fields each, fast to generate, can do 50-80 per agent
- **Heavy categories** (한자어): 7 fields with etymology, ~40 per agent
- **Medium categories** (사자성어): 6 fields, MUST validate exactly 4 syllables, ~30 per agent
- **Enrichment agents**: Read existing category, add `notes` field to each entry, write to `data/enriched_<name>.json`
- Run 5 agents in parallel (one per category) for maximum throughput
- Use haiku model for faster generation of light/topic entries

### Quality Checks
- No loanwords in 한자어 (words like 알고리즘, 서버 are NOT Sino-Korean)
- 사자성어 must be EXACTLY 4 Korean syllables and 4 hanja characters
- No duplicate `korean` values across categories
- All example sentences should be natural Korean, not textbook-stilted
- Batch file format: `{"category name": [{...},...]}` NOT `{key:..., entries:...}`
- All 104 categories should have `notes` field on every entry

## Current Stats
- Vocab: 5005 entries across 104 categories (all enriched with notes)
- Grammar: 101 patterns across 8 categories
- Fluency drills: 60 error correction + 50 grammar context + 30 reading + 40 register = 180 total
- Target: continue enriching and expanding drill content

## Key Design Decisions
- Self-rated flashcards (Anki-style reveal + rate), NOT auto-graded (except grammar fill-in-the-blank and grammar context)
- Comparison cards (" vs ") always show Korean→English to avoid exposing the answer
- User's guess is displayed alongside the correct answer after reveal
- User is semi-fluent; no beginner content, no travel phrases, no kdrama vocab
- UTF-8 encoding required explicitly on Windows (Python CLI)
- Firebase sync uses anonymous auth; progress merges by latest `last_review` timestamp
- All fluency drills (sentence production, error correction, grammar context, reading, register) are SRS-tracked

## Deployment
- GitHub Pages: Settings → Pages → Source: Deploy from branch, Branch: main, Folder: /docs
- Firebase: User must create Firebase project and paste config into index.html
- After any data change: always copy `data/*.json` → `docs/data/` before committing
