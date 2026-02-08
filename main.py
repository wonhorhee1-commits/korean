#!/usr/bin/env python3
"""Korean Coach — Advanced Fluency Trainer."""

import random
import sys

import ui
from srs import SRSEngine, GOOD
import vocab
import grammar


def mixed_review(srs: SRSEngine):
    """Mixed review pulling from both vocab and grammar, prioritizing weak cards."""
    vocab_data = vocab.load_vocab()
    grammar_data = grammar.load_grammar()

    # Build full pool
    pool = []
    for cat, entries in vocab_data.items():
        for i, entry in enumerate(entries):
            pool.append((vocab.card_id(cat, i), "vocab", cat, entry))
    for cat, entries in grammar_data.items():
        for i, entry in enumerate(entries):
            pool.append((grammar.card_id(cat, i), "grammar", cat, entry))

    all_ids = [cid for cid, _, _, _ in pool]
    due_ids = set(srs.get_due_cards(all_ids))

    due_pool = [item for item in pool if item[0] in due_ids]
    random.shuffle(due_pool)
    session_cards = due_pool[:15]

    if len(session_cards) < 15:
        rest = [item for item in pool if item[0] not in due_ids]
        random.shuffle(rest)
        session_cards.extend(rest[:15 - len(session_cards)])

    if not session_cards:
        ui.console.print("[dim]No cards available.[/dim]")
        ui.pause()
        return

    reviewed = 0
    correct = 0

    for cid, kind, cat, entry in session_cards:
        ui.clear()
        ui.console.print(f"[dim]{cat}[/dim]  [dim]({reviewed + 1}/{len(session_cards)})[/dim]\n")

        if kind == "vocab":
            korean = entry["korean"]
            english = entry["english"]

            is_comparison = " vs " in korean

            if is_comparison or random.random() < 0.5:
                ui.show_card_prompt(korean, hint=entry.get("hanja"))
                ui.console.print("[dim]What does this mean?[/dim]\n")
                user_answer = ui.ask("Your answer")
                if user_answer.strip().lower() == "q":
                    break
                ui.console.print()
                ui.show_answer(english, explanation=entry.get("notes"))
            else:
                ui.show_card_prompt(english)
                ui.console.print("[dim]What is this in Korean?[/dim]\n")
                user_answer = ui.ask("Your answer")
                if user_answer.strip().lower() == "q":
                    break
                ui.console.print()
                ui.show_answer(korean, explanation=entry.get("notes"))

            if "breakdown" in entry:
                ui.show_breakdown(entry["breakdown"])

            if "example" in entry:
                ui.show_example(entry["example"], entry.get("example_en"))

        elif kind == "grammar":
            pattern = entry["pattern"]
            meaning = entry["meaning"]
            explanation = entry["explanation"]
            examples = entry.get("examples", [])
            drill = entry.get("drill")

            ui.show_card_prompt(pattern)
            ui.console.print("[dim]What does this pattern mean?[/dim]\n")
            user_answer = ui.ask("Your answer")
            if user_answer.strip().lower() == "q":
                break
            ui.console.print()
            ui.show_answer(meaning, explanation=explanation)
            ui.console.print()

            for ex in examples:
                ui.show_example(ex["korean"], ex.get("english"))

            if drill:
                ui.console.print("[bold bright_cyan]Fill in the blank:[/bold bright_cyan]")
                ui.console.print(f"  {drill['prompt']}\n")
                user_drill = ui.ask("Answer")
                if user_drill.strip().lower() == "q":
                    break
                ui.console.print()
                is_correct = user_drill.strip() == drill["answer"]
                ui.show_result(is_correct, drill["answer"])
                ui.show_example(drill["full_sentence"])
                ui.console.print()

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


def view_progress(srs: SRSEngine):
    ui.clear()
    ui.banner()
    stats = srs.get_stats()
    ui.show_stats(stats)

    # Show weakest cards
    if srs.cards:
        weak = sorted(srs.cards.values(), key=lambda c: c.ease_factor)[:10]
        ui.console.print("[bold]Weakest Cards[/bold]\n")
        from rich.table import Table
        from rich import box
        table = Table(box=box.SIMPLE, border_style="dim")
        table.add_column("Card", style="white")
        table.add_column("Accuracy", justify="right", style="bright_yellow")
        table.add_column("Reviews", justify="right", style="dim")
        table.add_column("Ease", justify="right", style="dim")
        for card in weak:
            # Extract readable name from card_id
            parts = card.card_id.split(":", 2)
            name = parts[2] if len(parts) > 2 else card.card_id
            # Try to resolve to actual content
            label = _resolve_card_label(card.card_id)
            table.add_row(
                label,
                f"{card.accuracy:.0%}",
                str(card.total_reviews),
                f"{card.ease_factor:.1f}",
            )
        ui.console.print(table)
    ui.console.print()
    ui.pause()


def _resolve_card_label(card_id: str) -> str:
    """Try to get a human-readable label for a card ID."""
    parts = card_id.split(":")
    if len(parts) < 3:
        return card_id
    kind, category, idx_str = parts[0], parts[1], parts[2]
    try:
        idx = int(idx_str)
    except ValueError:
        return card_id
    if kind == "vocab":
        data = vocab.load_vocab()
        if category in data and idx < len(data[category]):
            return data[category][idx]["korean"]
    elif kind == "grammar":
        data = grammar.load_grammar()
        if category in data and idx < len(data[category]):
            return data[category][idx]["pattern"]
    return card_id


def main():
    srs = SRSEngine()

    while True:
        ui.clear()
        ui.banner()

        stats = srs.get_stats()
        if stats["total"] > 0:
            ui.console.print(
                f"[dim]Cards: {stats['total']}  |  "
                f"Due: {stats['due']}  |  "
                f"Accuracy: {stats['accuracy']:.0%}[/dim]\n"
            )

        choice = ui.menu([
            "Vocabulary Drill",
            "Grammar Practice",
            "Mixed Review (weakest items first)",
            "View Progress",
            "Quit",
        ])

        if choice == 0:
            vocab.run_drill(srs)
        elif choice == 1:
            grammar.run_drill(srs)
        elif choice == 2:
            mixed_review(srs)
        elif choice == 3:
            view_progress(srs)
        elif choice == 4:
            ui.clear()
            ui.console.print("[dim]수고하셨습니다! 다음에 또 만나요.[/dim]\n")
            sys.exit(0)


if __name__ == "__main__":
    main()
