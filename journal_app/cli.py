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


def search_entries():
    """CLI function to search entries by date or keyword."""
    console.print("\n[bold blue]--- Search Journal Entries ---[/bold blue]")
    search_type = console.input("[bold yellow]Search by [D]ate or [K]eyword? (D/K): [/bold yellow]").lower()

    session = get_session()
    try:
        if search_type == 'd':
            date_str = console.input("[bold yellow]Enter date (YYYY-MM-DD): [/bold yellow]").strip()
            try:
                search_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                console.print("[red]Invalid date format. Please use YYYY-MM-DD.[/red]")
                return

            entries = session.query(Entry).filter(
                Entry.date.like(f"{date_str}%") 
            ).order_by(Entry.date.desc()).all()

            if not entries:
                console.print(f"[yellow]No entries found for date {date_str}.[/yellow]")
                return
            console.print(f"[bold blue]--- Entries for {date_str} ---[/bold blue]")

        elif search_type == 'k':
            keyword = console.input("[bold yellow]Enter keyword: [/bold yellow]").strip()
            if not keyword:
                console.print("[red]Keyword cannot be empty. Aborting.[/red]")
                return
            
            # Using ilike for case-insensitive search
            entries = session.query(Entry).filter(
                or_(
                    Entry.title.ilike(f'%{keyword}%'),
                    Entry.content.ilike(f'%{keyword}%')
                )
            ).order_by(Entry.date.desc()).all()

            if not entries:
                console.print(f"[yellow]No entries found containing '{keyword}'.[/yellow]")
                return
            console.print(f"[bold blue]--- Entries containing '{keyword}' ---[/bold blue]")

        else:
            console.print("[red]Invalid search type. Please choose 'D' or 'K'.[/red]")
            return

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
        console.print(f"[red]Error searching entries: {e}[/red]")
    finally:
        session.close()

def update_entry():
    """CLI function to update an existing journal entry."""
    console.print("\n[bold blue]--- Update Journal Entry ---[/bold blue]")
    try:
        entry_id = int(console.input("[bold yellow]Enter Entry ID to update: [/bold yellow]"))
    except ValueError:
        console.print("[red]Invalid ID. Please enter a number.[/red]")
        return

    session = get_session()
    try:
        entry = session.query(Entry).filter_by(id=entry_id).first()
        if not entry:
            console.print(f"[red]Entry with ID {entry_id} not found.[/red]")
            return

        console.print(f"[green]Found Entry (ID: {entry.id}): {entry.title}[/green]")
        console.print("[bold yellow]Enter new title (leave blank to keep current): [/bold yellow]")
        new_title = console.input().strip()
        if new_title:
            entry.title = new_title

        console.print("[bold yellow]Enter new content (leave blank to keep current): [/bold yellow]")
        new_content = console.input().strip()
        if new_content:
            entry.content = new_content

        session.commit()
        console.print(f"[green]Entry ID {entry_id} updated successfully.[/green]")

        # Option to update tags
        console.print("[bold cyan]Do you want to modify tags for this entry? (y/n)[/bold cyan]")
        if console.input().lower() == 'y':
            manage_tags_for_entry(entry.id, session)

    except Exception as e:
        session.rollback()
        console.print(f"[red]Error updating entry: {e}[/red]")
    finally:
        session.close()

def delete_entry():
    """CLI function to delete a journal entry."""
    console.print("\n[bold blue]--- Delete Journal Entry ---[/bold blue]")
    try:
        entry_id = int(console.input("[bold yellow]Enter Entry ID to delete: [/bold yellow]"))
    except ValueError:
        console.print("[red]Invalid ID. Please enter a number.[/red]")
        return

    session = get_session()
    try:
        entry = session.query(Entry).filter_by(id=entry_id).first()
        if not entry:
            console.print(f"[red]Entry with ID {entry_id} not found.[/red]")
            return

        confirm = console.input(f"[bold red]Are you sure you want to delete '{entry.title}' (ID: {entry.id})? (y/n): [/bold red]").lower()
        if confirm == 'y':
            session.delete(entry)
            session.commit()
            console.print(f"[green]Entry ID {entry_id} deleted successfully.[/green]")
        else:
            console.print("[yellow]Deletion cancelled.[/yellow]")

    except Exception as e:
        session.rollback()
        console.print(f"[red]Error deleting entry: {e}[/red]")
    finally:
        session.close()

def create_tag():
    """CLI function to create a new tag."""
    console.print("\n[bold blue]--- Create New Tag ---[/bold blue]")
    tag_name = console.input("[bold yellow]Enter new tag name: [/bold yellow]").strip().capitalize()
    if not tag_name:
        console.print("[red]Tag name cannot be empty. Aborting.[/red]")
        return

    session = get_session()
    try:
        # Check if tag already exists
        existing_tag = session.query(Tag).filter_by(name=tag_name).first()
        if existing_tag:
            console.print(f"[yellow]Tag '{tag_name}' already exists with ID {existing_tag.id}.[/yellow]")
        else:
            new_tag = Tag(name=tag_name)
            session.add(new_tag)
            session.commit()
            console.print(f"[green]Tag '{tag_name}' created successfully with ID {new_tag.id}.[/green]")
    except Exception as e:
        session.rollback()
        console.print(f"[red]Error creating tag: {e}[/red]")
    finally:
        session.close()

def list_all_tags(session: Session = None):
    """Lists all available tags. Can use an existing session or open a new one."""
    close_session_after = False
    if session is None:
        session = get_session()
        close_session_after = True

    try:
        tags = session.query(Tag).order_by(Tag.name).all()
        if not tags:
            console.print("[yellow]No tags found.[/yellow]")
            return []
        
        console.print("\n[bold blue]--- All Available Tags ---[/bold blue]")
        tag_data = []
        for tag in tags:
            tag_data.append((str(tag.id), tag.name))
            console.print(f"[cyan]ID: {tag.id}[/cyan], [yellow]Name: {tag.name}[/yellow]")
        console.print("[bold blue]--------------------------\n[/bold blue]")
        return tags 
    except Exception as e:
        console.print(f"[red]Error listing tags: {e}[/red]")
        return []
    finally:
        if close_session_after:
            session.close()

def assign_tags_to_entry_by_id(entry_id: int, session: Session):
    """Helper to assign tags to a specific entry ID."""
    entry = session.query(Entry).filter_by(id=entry_id).first()
    if not entry:
        console.print(f"[red]Entry with ID {entry_id} not found.[/red]")
        return

    console.print(f"\n[bold blue]--- Assign/Remove Tags for Entry '{entry.title}' (ID: {entry.id}) ---[/bold blue]")
    
    current_tags = {tag.name for tag in entry.tags}
    if current_tags:
        console.print(f"[yellow]Current Tags:[/yellow] {', '.join(current_tags)}")
    else:
        console.print("[yellow]No current tags.[/yellow]")

    available_tags = list_all_tags(session) 

    if not available_tags:
        console.print("[yellow]No tags available to assign. Create some first![/yellow]")
        return

    console.print("[bold cyan]Enter tag names (comma-separated) to ADD or REMOVE. Press Enter to finish.[/bold cyan]")
    console.print("[bold cyan]Example: 'tag1, +new_tag, -old_tag'[/bold cyan]")
    
    tag_input = console.input("[bold yellow]Tags: [/bold yellow]").strip()

    if not tag_input:
        console.print("[yellow]No tags entered. Skipping tag assignment.[/yellow]")
        return

    tags_to_add = []
    tags_to_remove = []

    for tag_name in [t.strip() for t in tag_input.split(',') if t.strip()]:
        if tag_name.startswith('+'):
            tags_to_add.append(tag_name[1:]) # Add tag
        elif tag_name.startswith('-'):
            tags_to_remove.append(tag_name[1:]) # Remove tag
        else:
            tags_to_add.append(tag_name) # Default to add 

    for name in set(tags_to_add): # Use set to handle duplicates
        tag_obj = session.query(Tag).filter_by(name=name.capitalize()).first()
        if not tag_obj:
            console.print(f"[yellow]Tag '{name.capitalize()}' does not exist. Creating it.[/yellow]")
            tag_obj = Tag(name=name.capitalize())
            session.add(tag_obj)
            session.flush() # Ensure new tag has an ID before relating
        if tag_obj not in entry.tags:
            entry.tags.append(tag_obj)
            console.print(f"[green]Assigned tag '{tag_obj.name}' to entry.[/green]")
        else:
            console.print(f"[yellow]Entry already has tag '{tag_obj.name}'.[/yellow]")

    for name in set(tags_to_remove):
        tag_obj = session.query(Tag).filter_by(name=name.capitalize()).first()
        if tag_obj and tag_obj in entry.tags:
            entry.tags.remove(tag_obj)
            console.print(f"[green]Removed tag '{tag_obj.name}' from entry.[/green]")
        else:
            console.print(f"[yellow]Entry does not have tag '{name.capitalize()}' to remove, or tag not found.[/yellow]")

    session.commit()
    console.print(f"[green]Tags for Entry ID {entry_id} updated successfully.[/green]")

def manage_tags_for_entry(entry_id: int, session: Session = None):
    """Entry point for managing tags, can be called internally or via menu."""
    close_session_after = False
    if session is None:
        session = get_session()
        close_session_after = True
    try:
        assign_tags_to_entry_by_id(entry_id, session)
    except Exception as e:
        session.rollback()
        console.print(f"[red]Error managing tags for entry: {e}[/red]")
    finally:
        if close_session_after:
            session.close()

def view_entries_by_tag():
    """CLI function to view entries filtered by a specific tag."""
    console.print("\n[bold blue]--- View Entries by Tag ---[/bold blue]")
    
    session = get_session()
    try:
        tags = list_all_tags(session) # List available tags
        if not tags:
            console.print("[yellow]No tags available to filter by.[/yellow]")
            return

        tag_name_input = console.input("[bold yellow]Enter tag name to filter by: [/bold yellow]").strip().capitalize()
        if not tag_name_input:
            console.print("[red]Tag name cannot be empty. Aborting.[/red]")
            return

        tag = session.query(Tag).filter_by(name=tag_name_input).first()
        if not tag:
            console.print(f"[red]Tag '{tag_name_input}' not found.[/red]")
            return

        entries = tag.entries 
        if not entries:
            console.print(f"[yellow]No entries found for tag '{tag_name_input}'.[/yellow]")
            return

        console.print(f"[bold blue]--- Entries tagged '{tag_name_input}' ---[/bold blue]")
        table = RichTable(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=5)
        table.add_column("Date", style="cyan", width=18)
        table.add_column("Title", style="green", max_width=40)
        table.add_column("Tags", style="yellow") 

        for entry in entries:
            tag_names = ", ".join([t.name for t in entry.tags]) if entry.tags else "None"
            table.add_row(
                str(entry.id),
                entry.date.strftime('%Y-%m-%d %H:%M'),
                entry.title,
                tag_names
            )
        console.print(table)
        console.print("[bold blue]---------------------------\n[/bold blue]")

    except Exception as e:
        console.print(f"[red]Error viewing entries by tag: {e}[/red]")
    finally:
        session.close()

def demonstrate_data_structures():
    """A helper function to show explicit use of lists, dicts, tuples."""
    console.print("\n[bold green]--- Demonstrating Data Structures ---[/bold green]")

    operations = [
        "Create Entry",
        "View All Entries",
        "Search Entries",
        "Update Entry",
        "Delete Entry"
    ]
    console.print(f"List of operations (list): {operations}")
    
    entry_data = {
        "title": "My Day's Reflection",
        "content": "Learned a lot about Python ORM.",
        "date": datetime.now().strftime('%Y-%m-%d')
    }
    console.print(f"Entry data (dictionary): {entry_data}")
    
    valid_search_types = ('d', 'k')
    console.print(f"Valid search types (tuple): {valid_search_types}")
    def get_entry_summary(entry_id_val, title_val):
        return (entry_id_val, title_val)

    example_summary = get_entry_summary(101, "First Entry Title")
    console.print(f"Entry summary (tuple): {example_summary}")
    console.print("[bold green]-------------------------------------[/bold green]")