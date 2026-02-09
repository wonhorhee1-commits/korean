# Korean Coach — Development Guide

## Project Overview
Korean learning tool for an intermediate/advanced speaker targeting full fluency. Two interfaces:
- **Web app** (`docs/index.html`) — GitHub Pages, the primary interface
- **CLI** (`python main.py`) — Rich-based terminal UI, secondary

## Architecture
- `docs/index.html` — Single-file web app (HTML/CSS/JS, no build step)
- `docs/data/vocab.json` & `docs/data/grammar.json` — Data served by GitHub Pages
- `data/vocab.json` & `data/grammar.json` — Source of truth for data
- `data/batch_*.json` — Intermediate batch files from expansion runs
- `merge_data.py` — Merges batch files into main data, syncs to `docs/data/`
- SM-2 spaced repetition algorithm (same as Anki)
- Firebase anonymous auth + Firestore for cross-device sync (config in index.html)

## Data Format

### Vocab Categories & Required Fields
| Category | Fields |
|---|---|
| 한자어 (Sino-Korean) | korean, english, hanja, breakdown, example, example_en, notes |
| 뉘앙스 & 유의어 | korean (must contain " vs "), english, example, example_en |
| 격식 & 문어체 | korean, english, example, example_en |
| 사자성어 (Four-Character Idioms) | korean (EXACTLY 4 syllables), english, hanja (EXACTLY 4 chars), breakdown, example, example_en |
| 관용어 (Korean Idioms) | korean, english, example, example_en |

### Grammar Format
Each pattern: pattern, meaning, explanation, examples (array of {korean, english}), drill ({prompt, answer, full_sentence})

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
- Run 5 agents in parallel (one per category) for maximum throughput

### Quality Checks
- No loanwords in 한자어 (words like 알고리즘, 서버 are NOT Sino-Korean)
- 사자성어 must be EXACTLY 4 Korean syllables and 4 hanja characters
- No duplicate `korean` values across categories
- All example sentences should be natural Korean, not textbook-stilted

## Current Stats
- Vocab: 544 entries (한자어 148, 뉘앙스 100, 격식 100, 사자성어 75, 관용어 121)
- Grammar: 41 patterns across 5 categories
- Target: 1000+ vocab across multiple sessions

## Key Design Decisions
- Self-rated flashcards (Anki-style reveal + rate), NOT auto-graded (except grammar fill-in-the-blank)
- Comparison cards (" vs ") always show Korean→English to avoid exposing the answer
- User's guess is displayed alongside the correct answer after reveal
- User is semi-fluent; no beginner content, no travel phrases, no kdrama vocab
- UTF-8 encoding required explicitly on Windows (Python CLI)
- Firebase sync uses anonymous auth; progress merges by latest `last_review` timestamp

## Deployment
- GitHub Pages: Settings → Pages → Source: Deploy from branch, Branch: main, Folder: /docs
- Firebase: User must create Firebase project and paste config into index.html
