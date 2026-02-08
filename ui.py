"""Rich-based UI helpers for the Korean Coach."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt
from rich import box

console = Console()


def clear():
    console.clear()


def banner():
    title = Text("한국어 코치", style="bold bright_white")
    subtitle = Text("Korean Coach — Advanced Fluency Trainer", style="dim")
    content = Text.assemble(title, "\n", subtitle)
    console.print(Panel(content, box=box.DOUBLE, border_style="bright_blue", padding=(1, 4)))
    console.print()


def menu(options: list[str]) -> int:
    """Display a numbered menu and return the selected index (0-based)."""
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column(style="bright_cyan bold", width=4)
    table.add_column(style="white")
    for i, option in enumerate(options, 1):
        table.add_row(f"[{i}]", option)
    console.print(table)
    console.print()

    while True:
        choice = Prompt.ask("[bright_cyan]Choose[/]", default="1")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return idx
        except ValueError:
            pass
        console.print("[red]Invalid choice.[/]")


def ask(prompt_text: str, default: str | None = None) -> str:
    """Ask for input. Returns 'q' if user wants to quit."""
    result = Prompt.ask(f"[bright_cyan]{prompt_text}[/] [dim](q to quit)[/]", default=default or "")
    return result


def show_card_prompt(korean: str, hint: str | None = None):
    """Display a card prompt — the thing being quizzed."""
    parts = [Text(korean, style="bold bright_white on grey23")]
    if hint:
        parts.append(Text(f"\n{hint}", style="dim italic"))
    content = Text.assemble(*parts)
    console.print(Panel(content, box=box.ROUNDED, border_style="bright_blue", padding=(1, 3)))


def show_answer(answer: str, explanation: str | None = None):
    """Reveal the answer (self-rated, no correct/incorrect judgment)."""
    parts = [Text(answer, style="bold white")]
    if explanation:
        parts.append(Text(f"\n{explanation}", style="dim"))
    content = Text.assemble(*parts)
    console.print(Panel(content, box=box.ROUNDED, border_style="bright_blue", padding=(0, 2)))


def show_result(correct: bool, answer: str, explanation: str | None = None):
    if correct:
        mark = Text("✓ Correct!", style="bold bright_green")
    else:
        mark = Text("✗ Incorrect", style="bold bright_red")

    parts = [mark, Text(f"\n{answer}", style="white")]
    if explanation:
        parts.append(Text(f"\n{explanation}", style="dim"))
    content = Text.assemble(*parts)
    style = "bright_green" if correct else "bright_red"
    console.print(Panel(content, box=box.ROUNDED, border_style=style, padding=(0, 2)))


def show_breakdown(breakdown: str):
    """Show hanja syllable breakdown for Sino-Korean words."""
    console.print(f"  [bright_magenta]한자 breakdown:[/] [white]{breakdown}[/]")


def show_example(sentence: str, translation: str | None = None):
    parts = [Text(f"  {sentence}", style="italic bright_yellow")]
    if translation:
        parts.append(Text(f"\n  {translation}", style="dim"))
    console.print(Text.assemble(*parts))
    console.print()


def show_stats(stats: dict):
    table = Table(title="Progress", box=box.ROUNDED, border_style="bright_blue")
    table.add_column("Metric", style="bright_cyan")
    table.add_column("Value", style="white", justify="right")
    table.add_row("Cards Seen", str(stats["total"]))
    table.add_row("Due Now", str(stats["due"]))
    table.add_row("Learning (<7d)", str(stats["learning"]))
    table.add_row("Mature (≥7d)", str(stats["mature"]))
    table.add_row("Accuracy", f"{stats['accuracy']:.0%}")
    console.print(table)
    console.print()


def show_session_summary(reviewed: int, correct: int):
    acc = correct / reviewed if reviewed > 0 else 0
    if acc >= 0.9:
        grade_style = "bold bright_green"
        comment = "Excellent."
    elif acc >= 0.7:
        grade_style = "bold bright_yellow"
        comment = "Solid, but room to sharpen."
    elif acc >= 0.5:
        grade_style = "bold yellow"
        comment = "Getting there. Keep drilling."
    else:
        grade_style = "bold bright_red"
        comment = "These need more work. They'll come back."

    table = Table(box=box.ROUNDED, border_style="bright_blue", title="Session Complete")
    table.add_column("", style="bright_cyan")
    table.add_column("", justify="right")
    table.add_row("Reviewed", str(reviewed))
    table.add_row("Correct", str(correct))
    table.add_row("Accuracy", Text(f"{acc:.0%}", style=grade_style))
    console.print(table)
    console.print(Text(f"  {comment}", style="dim italic"))
    console.print()


def rating_prompt() -> int | None:
    """Ask the user to self-rate after seeing the answer. Returns SRS quality."""
    from srs import AGAIN, HARD, GOOD, EASY
    console.print(
        "  [bright_red][1] Again[/] [dim]didn't know[/]  "
        "[yellow][2] Hard[/] [dim]struggled[/]  "
        "[bright_green][3] Good[/] [dim]knew it[/]  "
        "[bright_cyan][4] Easy[/] [dim]effortless[/]"
    )
    while True:
        choice = Prompt.ask("[dim]Rate[/]", default="3")
        mapping = {"1": AGAIN, "2": HARD, "3": GOOD, "4": EASY}
        if choice in mapping:
            return mapping[choice]
        if choice.lower() == "q":
            return None
        console.print("[red]Enter 1-4 or q to quit.[/]")


def pause():
    Prompt.ask("[dim]Press Enter to continue[/]", default="")
