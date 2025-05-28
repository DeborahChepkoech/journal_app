from journal_app.database import create_db_and_tables
from journal_app.cli import (
    add_entry, view_all_entries, view_entry_details, search_entries,
    update_entry, delete_entry, create_tag, manage_tags_for_entry,
    view_entries_by_tag, delete_tag
)
from rich.console import Console 

console = Console()

def display_menu():
    """Displays the main menu options to the user."""
    console.print("\n[bold green]--- Journal App Menu ---[/bold green]")
    console.print("[bold cyan]1.[/bold cyan] Add New Entry")
    console.print("[bold cyan]2.[/bold cyan] View All Entries")
    console.print("[bold cyan]3.[/bold cyan] View Entry Details (by ID)")
    console.print("[bold cyan]4.[/bold cyan] Search Entries")
    console.print("[bold cyan]5.[/bold cyan] Update Entry")
    console.print("[bold cyan]6.[/bold cyan] Delete Entry")
    console.print("[bold cyan]7.[/bold cyan] Create New Tag")
    console.print("[bold cyan]8.[/bold cyan] Manage Tags for Entry")
    console.print("[bold cyan]9.[/bold cyan] View Entries by Tag")
    console.print("[bold cyan]10.[/bold cyan] Delete Tag")
    console.print("[bold red]Q.[/bold red] Quit")
    console.print("[bold green]------------------------[/bold green]")

def run_application():
    """Main loop for the CLI application."""
    create_db_and_tables() 

    while True:
        display_menu()
        choice = console.input("[bold yellow]Enter your choice: [/bold yellow]").strip().upper()

        if choice == '1':
            add_entry()
        elif choice == '2':
            view_all_entries()
        elif choice == '3':
            view_entry_details()
        elif choice == '4':
            search_entries()
        elif choice == '5':
            update_entry()
        elif choice == '6':
            delete_entry()
        elif choice == '7':
            create_tag()
        elif choice == '8':
            try:
                entry_id = int(console.input("[bold yellow]Enter Entry ID to manage tags for: [/bold yellow]"))
                manage_tags_for_entry(entry_id)
            except ValueError:
                console.print("[red]Invalid ID. Please enter a number.[/red]")
        elif choice == '9':
            view_entries_by_tag()
        elif choice == '10': 
            delete_tag()
        elif choice == 'Q':
            console.print("[bold green]Exiting Journal App. Goodbye![/bold green]")
            break
        else:
            console.print("[red]Invalid choice. Please try again.[/red]")

if __name__ == "__main__":
    run_application()