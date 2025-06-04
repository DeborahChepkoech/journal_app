from journal_app.database import create_db_and_tables
from journal_app.cli import (
    add_entry, view_all_entries, view_entry_details, search_entries,
    update_entry, delete_entry, create_tag, manage_tags_for_entry, delete_tag
)
from rich.console import Console 

console = Console()

def display_menu():
    """Displays the main menu options to the user."""
    console.print("\n--- Journal App Menu ---")
    console.print("1. Add New Entry")
    console.print("2. View All Entries")
    console.print("3. View Entry Details (by ID)")
    console.print("4. Search Entries")
    console.print("5. Update Entry")
    console.print("6. Delete Entry")
    console.print("7. Create New Tag")
    console.print("8. Manage Tags for Entry")
    console.print("9. Delete Tag")
    console.print("[bold red]Q.[/bold red] Quit")
    console.print("------------------------")

def run_application():
    """Main loop for the CLI application."""
    create_db_and_tables() 

    while True:
        display_menu()
        choice = console.input("Enter your choice: ").strip().upper()

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
                entry_id = int(console.input("Enter Entry ID to manage tags for: "))
                manage_tags_for_entry(entry_id)
            except ValueError:
                console.print("[red]Invalid ID. Please enter a number.[/red]")
        elif choice == '9': 
            delete_tag()
        elif choice == 'Q':
            console.print("Exiting Journal App. Goodbye!")
            break
        else:
            console.print("[red]Invalid choice. Please try again.[/red]")

if __name__ == "__main__":
    run_application()