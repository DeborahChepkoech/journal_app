from datetime import datetime
from sqlalchemy import or_ 
from sqlalchemy.orm import Session
from .models import Entry, Tag
from .database import get_session
from rich.console import Console # For better CLI output
from rich.table import Table as RichTable
from rich.text import Text 

console = Console()


def add_entry():
    """CLI function to add a new journal entry."""
    console.print("\n--- Add New Journal Entry ---")

    title = console.input("Enter title:").strip()
    if not title or title.lower() in ('q', 'quit'):
        console.print("Operation cancelled. Returning to main menu.")
        return
    
    content = console.input("Enter content:").strip()
    if not content or content.lower() in ('q', 'quit'):
        console.print("Operation cancelled. Returning to main menu.")
        return

    privacy_choice = console.input("Make this entry [P]rivate or [U]ublic? (P/U, default Private):").strip().lower()
    is_private_status = True 
    if privacy_choice == 'u':
        is_private_status = False
    elif privacy_choice in ('q', 'quit'):
        console.print("Operation cancelled. Returning to main menu.")
        return
    

    session: Session = get_session()
    try:
        new_entry = Entry(title=title, content=content, is_private=is_private_status) 
        session.add(new_entry)
        session.commit()
        console.print(f"Entry '{title}' created successfully with ID {new_entry.id}.")

        console.print("Do you want to add tags to this entry? (y/n)")
        tag_choice = console.input().lower()
        if tag_choice in ('y', 'q', 'quit'):
            if tag_choice in ('q', 'quit'):
                console.print("Skipping tag assignment. Returning to main menu.")
                return
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
            console.print("No entries found.")
            return

        console.print("\n--- All Journal Entries ---")
        table = RichTable(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=5)
        table.add_column("Date", style="cyan", width=18)
        table.add_column("Title", style="green", max_width=30)
        table.add_column("Status", style="purple", width=10) 
        table.add_column("Tags", style="yellow")

        for entry in entries:
            tag_names = ", ".join([tag.name for tag in entry.tags]) if entry.tags else "None"
            privacy_status = "Private" if entry.is_private else "Public" 
            table.add_row(
                str(entry.id),
                entry.date.strftime('%Y-%m-%d %H:%M'),
                entry.title,
                privacy_status, 
                tag_names
            )
        console.print(table)
        console.print("---------------------------\n")

    except Exception as e:
        console.print(f"[red]Error viewing entries: {e}[/red]")
    finally:
        session.close()
def view_entry_details():
    """CLI function to view full details of a specific entry by ID."""
    console.print("\n--- View Entry Details ---")
    try:
        entry_id = int(console.input("Enter Entry ID to view:"))
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
    console.print("\n--- Search Journal Entries ---")

    search_type = console.input("Search by [D]ate or [K]eyword? (D/K):").strip().lower()
    if search_type in ('q', 'quit'):
        console.print("Operation cancelled. Returning to main menu.")
        return

    session = get_session()
    try:
        entries = [] 

        if search_type == 'd':
            date_str = console.input("Enter date (YYYY-MM-DD): ").strip()
            if date_str.lower() in ('q', 'quit'):
                console.print("Operation cancelled. Returning to main menu.")
                return
            try:
                search_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                console.print("[red]Invalid date format. Please use YYYY-MM-DD or 'q' to quit.[/red]")
                return

            entries = session.query(Entry).filter(
                Entry.date.like(f"{date_str}%")
            ).order_by(Entry.date.desc()).all()

            if not entries:
                console.print(f"No entries found for date {date_str}.")
                return
            console.print(f"--- Entries for {date_str} ---")

        elif search_type == 'k':
            keyword = console.input("Enter keyword: ").strip()
            if not keyword or keyword.lower() in ('q', 'quit'):
                console.print("Operation cancelled. Returning to main menu.")
                return
            
            entries = session.query(Entry).filter(
                or_(
                    Entry.title.ilike(f'%{keyword}%'),
                    Entry.content.ilike(f'%{keyword}%')
                )
            ).order_by(Entry.date.desc()).all()

            if not entries:
                console.print(f"No entries found containing '{keyword}'.")
                return
            console.print(f"--- Entries containing '{keyword}' ---")

        else:
            console.print("[red]Invalid search type. Please choose 'D' or 'K' or 'q' to quit.[/red]")
            return

        table = RichTable(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=5)
        table.add_column("Date", style="cyan", width=18)
        table.add_column("Title", style="green", max_width=30)
        table.add_column("Status", style="purple", width=10)
        table.add_column("Tags", style="yellow")

        for entry in entries:
            tag_names = ", ".join([tag.name for tag in entry.tags]) if entry.tags else "None"
            privacy_status = "Private" if entry.is_private else "Public" 
            table.add_row(
                str(entry.id),
                entry.date.strftime('%Y-%m-%d %H:%M'),
                entry.title,
                privacy_status, 
                tag_names
            )
        console.print(table)
        console.print("---------------------------\n")

    except Exception as e:
        console.print(f"[red]Error searching entries: {e}[/red]")
    finally:
        session.close()

def update_entry():
    """CLI function to update an existing journal entry."""
    console.print("\n--- Update Journal Entry ---")
    console.print("[dim]Type 'q' or 'quit' to return to the main menu.[/dim]")

    entry_id_input = console.input("Enter Entry ID to update: ").strip()
    if entry_id_input.lower() in ('q', 'quit'):
        console.print("Operation cancelled. Returning to main menu.")
        return

    try:
        entry_id = int(entry_id_input)
    except ValueError:
        console.print("[red]Invalid ID. Please enter a number or 'q' to quit.[/red]")
        return

    session = get_session()
    try:
        entry = session.query(Entry).filter_by(id=entry_id).first()
        if not entry:
            console.print(f"[red]Entry with ID {entry_id} not found.[/red]")
            return

        console.print(f"Found Entry (ID: {entry.id}): {entry.title} ({'Private' if entry.is_private else 'Public'})")

        console.print("Enter new title (leave blank to keep current): ")
        new_title = console.input().strip()
        if new_title.lower() in ('q', 'quit'): return
        if new_title:
            entry.title = new_title

        console.print("Enter new content (leave blank to keep current): ")
        new_content = console.input().strip()
        if new_content.lower() in ('q', 'quit'): return 
        if new_content:
            entry.content = new_content

        current_privacy = "Private" if entry.is_private else "Public"
        privacy_change_choice = console.input(f"Current status is {current_privacy}. Change to [P]rivate or [U]ublic? (P/U, leave blank to keep current): ").strip().lower()
        if privacy_change_choice.lower() in ('q', 'quit'): return

        if privacy_change_choice == 'p':
            entry.is_private = True
            console.print("Status set to Private.")
        elif privacy_change_choice == 'u':
            entry.is_private = False
            console.print("Status set to Public.")
        elif privacy_change_choice == '': 
            pass
        else:
            console.print("Invalid privacy choice. Keeping current status.")
      

        session.commit()
        console.print(f"Entry ID {entry_id} updated successfully.")

        console.print("Do you want to modify tags for this entry? (y/n)")
        tag_manage_choice = console.input().lower()
        if tag_manage_choice in ('y', 'q', 'quit'):
            if tag_manage_choice in ('q', 'quit'):
                console.print("Skipping tag management. Returning to main menu.")
                return
            manage_tags_for_entry(entry.id, session)

    except Exception as e:
        session.rollback()
        console.print(f"[red]Error updating entry: {e}[/red]")
    finally:
        session.close()

def delete_entry():
    """CLI function to delete a journal entry."""
    console.print("\n--- Delete Journal Entry ---")
    try:
        entry_id = int(console.input("Enter Entry ID to delete: "))
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
            console.print(f"Entry ID {entry_id} deleted successfully.")
        else:
            console.print("Deletion cancelled.")

    except Exception as e:
        session.rollback()
        console.print(f"[red]Error deleting entry: {e}[/red]")
    finally:
        session.close()

def create_tag():
    """CLI function to create a new tag."""
    console.print("\n--- Create New Tag ---")
    tag_name = console.input("Enter new tag name: ").strip().capitalize()
    if not tag_name:
        console.print("[red]Tag name cannot be empty. Aborting.[/red]")
        return

    session = get_session()
    try:
    
        existing_tag = session.query(Tag).filter_by(name=tag_name).first()
        if existing_tag:
            console.print(f"Tag '{tag_name}' already exists with ID {existing_tag.id}.")
        else:
            new_tag = Tag(name=tag_name)
            session.add(new_tag)
            session.commit()
            console.print(f"Tag '{tag_name}' created successfully with ID {new_tag.id}.")
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
            console.print("No tags found.")
            return []
        
        console.print("\n--- All Available Tags ---")
        tag_data = []
        for tag in tags:
            tag_data.append((str(tag.id), tag.name))
            console.print(f"[cyan]ID: {tag.id}[/cyan], Name: {tag.name}")
        console.print("--------------------------\n")
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

    console.print(f"\n--- Assign/Remove Tags for Entry '{entry.title}' (ID: {entry.id}) ---")
    
    current_tags = {tag.name for tag in entry.tags}
    if current_tags:
        console.print(f"Current Tags: {', '.join(current_tags)}")
    else:
        console.print("No current tags.")

    available_tags = list_all_tags(session) 

    if not available_tags:
        console.print("No tags available to assign. Create some first!")
        return

    console.print("Enter tag names (comma-separated) to ADD or REMOVE. Press Enter to finish.")
    console.print("Example: 'tag1, +new_tag, -old_tag'")
    
    tag_input = console.input("Tags: ").strip()

    if not tag_input:
        console.print("No tags entered. Skipping tag assignment.")
        return

    tags_to_add = []
    tags_to_remove = []

    for tag_name in [t.strip() for t in tag_input.split(',') if t.strip()]:
        if tag_name.startswith('+'):
            tags_to_add.append(tag_name[1:]) 
        elif tag_name.startswith('-'):
            tags_to_remove.append(tag_name[1:]) 
        else:
            tags_to_add.append(tag_name) 

    for name in set(tags_to_add): 
        tag_obj = session.query(Tag).filter_by(name=name.capitalize()).first()
        if not tag_obj:
            console.print(f"Tag '{name.capitalize()}' does not exist. Creating it.")
            tag_obj = Tag(name=name.capitalize())
            session.add(tag_obj)
            session.flush() 
        if tag_obj not in entry.tags:
            entry.tags.append(tag_obj)
            console.print(f"Assigned tag '{tag_obj.name}' to entry.")
        else:
            console.print(f"Entry already has tag '{tag_obj.name}'.")

    for name in set(tags_to_remove):
        tag_obj = session.query(Tag).filter_by(name=name.capitalize()).first()
        if tag_obj and tag_obj in entry.tags:
            entry.tags.remove(tag_obj)
            console.print(f"Removed tag '{tag_obj.name}' from entry.")
        else:
            console.print(f"Entry does not have tag '{name.capitalize()}' to remove, or tag not found.")

    session.commit()
    console.print(f"Tags for Entry ID {entry_id} updated successfully.")

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

def delete_tag():
    """CLI function to delete an existing tag."""
    console.print("\n--- Delete Tag ---")
    
    session = get_session()
    try:
        console.print("Available Tags:")
        tags = list_all_tags(session)

        if not tags:
            console.print("No tags to delete.")
            return

        tag_name_or_id = console.input("Enter Tag Name or ID to delete: ").strip()
        if not tag_name_or_id:
            console.print("[red]Input cannot be empty. Aborting.[/red]")
            return

        tag_to_delete = None
        try:
            tag_id = int(tag_name_or_id)
            tag_to_delete = session.query(Tag).filter_by(id=tag_id).first()
        except ValueError:
            tag_to_delete = session.query(Tag).filter_by(name=tag_name_or_id.capitalize()).first()

        if not tag_to_delete:
            console.print(f"[red]Tag '{tag_name_or_id}' not found.[/red]")
            return
        confirm = console.input(
            f"[bold red]Are you sure you want to delete tag '{tag_to_delete.name}' (ID: {tag_to_delete.id})?\n"
            f"This will remove it from all entries it's currently assigned to. (y/n): [/bold red]"
        ).lower()

        if confirm == 'y':
            session.delete(tag_to_delete)
            session.commit()
            console.print(f"Tag '{tag_to_delete.name}' deleted successfully.")
        else:
            console.print("Tag deletion cancelled.")

    except Exception as e:
        session.rollback()
        console.print(f"[red]Error deleting tag: {e}[/red]")
    finally:
        session.close()

