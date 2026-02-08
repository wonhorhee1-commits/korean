"""Grammar drill module."""

import json
import random
from pathlib import Path

import ui
from srs import SRSEngine, GOOD

DATA_FILE = Path(__file__).parent / "data" / "grammar.json"


def load_grammar() -> dict[str, list[dict]]:
    return json.loads(DATA_FILE.read_text())


def card_id(category: str, idx: int) -> str:
    return f"grammar:{category}:{idx}"


def run_drill(srs: SRSEngine, session_size: int = 10):
    """Run a grammar drill session."""
    data = load_grammar()
    categories = list(data.keys())

    ui.clear()
    ui.banner()
    ui.console.print("[bold]Grammar Practice[/bold]\n")

    options = ["All Patterns"] + categories
    choice = ui.menu(options)

    if choice == 0:
        selected_categories = categories
    else:
        selected_categories = [categories[choice - 1]]

    # Build pool
    pool = []
    for cat in selected_categories:
        for i, entry in enumerate(data[cat]):
            pool.append((card_id(cat, i), cat, entry))

    all_ids = [cid for cid, _, _ in pool]
    due_ids = set(srs.get_due_cards(all_ids))

    due_pool = [item for item in pool if item[0] in due_ids]
    random.shuffle(due_pool)
    session_cards = due_pool[:session_size]

    if len(session_cards) < session_size:
        rest = [item for item in pool if item[0] not in due_ids]
        random.shuffle(rest)
        session_cards.extend(rest[:session_size - len(session_cards)])

    if not session_cards:
        ui.console.print("[dim]No patterns available.[/dim]")
        ui.pause()
        return

    reviewed = 0
    correct = 0

    for cid, cat, entry in session_cards:
        ui.clear()
        ui.console.print(f"[dim]{cat}[/dim]  [dim]({reviewed + 1}/{len(session_cards)})[/dim]\n")

        pattern = entry["pattern"]
        meaning = entry["meaning"]
        explanation = entry["explanation"]
        examples = entry.get("examples", [])
        drill = entry.get("drill")

        # Phase 1: Show pattern, ask for meaning
        ui.show_card_prompt(pattern)
        ui.console.print("[dim]What does this pattern mean?[/dim]\n")
        user_answer = ui.ask("Your answer")
        ui.console.print()

        # Reveal meaning + explanation
        ui.show_result(True, meaning, explanation=explanation)
        ui.console.print()

        # Show examples
        for ex in examples:
            ui.show_example(ex["korean"], ex.get("english"))

        # Phase 2: Fill-in drill if available
        if drill:
            ui.console.print("[bold bright_cyan]Fill in the blank:[/bold bright_cyan]")
            ui.console.print(f"  {drill['prompt']}\n")
            user_drill = ui.ask("Answer")
            ui.console.print()

            is_correct = user_drill.strip() == drill["answer"]
            ui.show_result(is_correct, drill["answer"])
            ui.show_example(drill["full_sentence"])
            ui.console.print()

        # Self-rating
        rating = ui.rating_prompt()
        if rating is None:
            break

        srs.record_review(cid, rating)
        reviewed += 1
        if rating >= GOOD:
            correct += 1

    ui.console.print()
    ui.show_session_summary(reviewed, correct)
    ui.pause()
