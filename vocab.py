"""Vocabulary drill module."""

import json
import random
from pathlib import Path

import ui
from srs import SRSEngine, GOOD

DATA_FILE = Path(__file__).parent / "data" / "vocab.json"


def load_vocab() -> dict[str, list[dict]]:
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def card_id(category: str, idx: int) -> str:
    return f"vocab:{category}:{idx}"


def run_drill(srs: SRSEngine, session_size: int = 15):
    """Run a vocabulary drill session."""
    data = load_vocab()
    categories = list(data.keys())

    ui.clear()
    ui.banner()
    ui.console.print("[bold]Vocabulary Drill[/bold]\n")

    # Let user pick category or all
    options = ["All Categories"] + categories
    choice = ui.menu(options)

    if choice == 0:
        selected_categories = categories
    else:
        selected_categories = [categories[choice - 1]]

    # Build card pool
    pool = []
    for cat in selected_categories:
        for i, entry in enumerate(data[cat]):
            pool.append((card_id(cat, i), cat, entry))

    all_ids = [cid for cid, _, _ in pool]
    due_ids = set(srs.get_due_cards(all_ids))

    # Prioritize due cards, then fill with others
    due_pool = [item for item in pool if item[0] in due_ids]
    random.shuffle(due_pool)
    session_cards = due_pool[:session_size]

    if len(session_cards) < session_size:
        rest = [item for item in pool if item[0] not in due_ids]
        random.shuffle(rest)
        session_cards.extend(rest[:session_size - len(session_cards)])

    if not session_cards:
        ui.console.print("[dim]No cards available.[/dim]")
        ui.pause()
        return

    reviewed = 0
    correct = 0

    for cid, cat, entry in session_cards:
        ui.clear()
        ui.console.print(f"[dim]{cat}[/dim]  [dim]({reviewed + 1}/{len(session_cards)})[/dim]\n")

        korean = entry["korean"]
        english = entry["english"]

        # Randomly choose direction
        if random.random() < 0.5:
            # Korean → English
            ui.show_card_prompt(korean, hint=entry.get("hanja"))
            ui.console.print("[dim]What does this mean?[/dim]\n")
            user_answer = ui.ask("Your answer")
            ui.console.print()
            ui.show_result(True, english, explanation=None)
        else:
            # English → Korean
            ui.show_card_prompt(english)
            ui.console.print("[dim]What is this in Korean?[/dim]\n")
            user_answer = ui.ask("Your answer")
            ui.console.print()
            ui.show_result(True, korean, explanation=entry.get("notes"))

        # Show example
        if "example" in entry:
            ui.show_example(entry["example"], entry.get("example_en"))

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
