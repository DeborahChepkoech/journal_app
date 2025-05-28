# journal_app/cli.py
from datetime import datetime
from sqlalchemy import or_ # For complex queries like OR
from sqlalchemy.orm import Session
from .models import Entry, Tag
from .database import get_session
from rich.console import Console # For better CLI output
from rich.table import Table as RichTable
from rich.text import Text 

console = Console()

def add_entry():
    """CLI function to add a new journal entry."""
    console.print("\n[bold blue]--- Add New Journal Entry ---[/bold blue]")
    title = console.input("[bold yellow]Enter title: [/bold yellow]").strip()
    if not title:
        console.print("[red]Title cannot be empty. Aborting.[/red]")
        return
    content = console.input("[bold yellow]Enter content: [/bold yellow]").strip()
    if not content:
        console.print("[red]Content cannot be empty. Aborting.[/red]")
        return

    session: Session = get_session() # Type hint for session
    try:
        new_entry = Entry(title=title, content=content)
        session.add(new_entry)
        session.commit()
        console.print(f"[green]Entry '{title}' created successfully with ID {new_entry.id}.[/green]")
        console.print("[bold cyan]Do you want to add tags to this entry? (y/n)[/bold cyan]")
        if console.input().lower() == 'y':
            assign_tags_to_entry_by_id(new_entry.id, session)

    except Exception as e:
        session.rollback()
        console.print(f"[red]Error adding entry: {e}[/red]")
    finally:
        session.close()

def view_all_entries():
    """CLI function to view all journal entries."""
    session = get_session()
    try:
        entries = session.query(Entry).order_by(Entry.date.desc()).all()
        if not entries:
            console.print("[yellow]No entries found.[/yellow]")
            return

        console.print("\n[bold blue]--- All Journal Entries ---[/bold blue]")
        table = RichTable(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=5)
        table.add_column("Date", style="cyan", width=18)
        table.add_column("Title", style="green", max_width=40)
        table.add_column("Tags", style="yellow")

        for entry in entries:
            tag_names = ", ".join([tag.name for tag in entry.tags]) if entry.tags else "None"
            table.add_row(
                str(entry.id),
                entry.date.strftime('%Y-%m-%d %H:%M'),
                entry.title,
                tag_names
            )
        console.print(table)
        console.print("[bold blue]---------------------------\n[/bold blue]")

    except Exception as e:
        console.print(f"[red]Error viewing entries: {e}[/red]")
    finally:
        session.close()

def view_entry_details():
    """CLI function to view full details of a specific entry by ID."""
    console.print("\n[bold blue]--- View Entry Details ---[/bold blue]")
    try:
        entry_id = int(console.input("[bold yellow]Enter Entry ID to view: [/bold yellow]"))
    except ValueError:
        console.print("[red]Invalid ID. Please enter a number.[/red]")
        return

    session = get_session()
    try:
        entry = session.query(Entry).filter_by(id=entry_id).first()
        if entry:
            console.print(entry.display())
        else:
            console.print(f"[red]Entry with ID {entry_id} not found.[/red]")
    except Exception as e:
        console.print(f"[red]Error viewing entry details: {e}[/red]")
    finally:
        session.close()


