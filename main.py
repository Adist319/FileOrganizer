# File Organizer
# A simple tool to organize files
import os
from FileOrganizer import FileOrganizer


def main():
    # Get the directory to organize from user input
    directory = input("Enter the directory path to organize: ")
    
    # Verify the directory exists
    if not os.path.isdir(directory):
        print("Error: Invalid directory path")
        return
    
    # Create organizer
    organizer = FileOrganizer(directory)
    
    while True:
        print("\nFile Organizer Menu:")
        print("1. Organize files")
        print("2. Undo last operation")
        print("3. Undo all operations")
        print("4. Show operation history")
        print("5. Add custom rule")
        print("6. Cleanup empty directories")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ")
        
        if choice == '1':
            organizer.organize_files()
        elif choice == '2':
            if organizer.undo_last():
                print("Successfully undid last operation")
            else:
                print("No operations to undo or undo failed")
        elif choice == '3':
            count = organizer.undo_all()
            print(f"Successfully undid {count} operations")
        elif choice == '4':
            history = organizer.get_operation_history()
            if history:
                print("\nOperation History:")
                for op in history:
                    print(f"{op['timestamp']}: Moved {op['file']}")
                    print(f"  From: {op['from']}")
                    print(f"  To: {op['to']}\n")
            else:
                print("No operation history available")
        elif choice == '5':
            pattern = input("Enter regex pattern (e.g., '\\.log$'): ")
            destination = input("Enter destination category: ")
            organizer.add_custom_rule(pattern, destination)
        elif choice == '6':
            removed = organizer.cleanup_empty_directories()
            if removed:
                print(f"Removed empty directories: {', '.join(removed)}")
            else:
                print("No empty directories to remove")
        elif choice == '7':
            break
        else:
            print("Invalid choice. Please try again.")
    print("Thanks for using File Organizer!")

if __name__ == "__main__":
    main()