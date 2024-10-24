import os
import shutil
from pathlib import Path
import logging
from datetime import datetime
import json
from collections import defaultdict
import re

class FileOperation:
    def __init__(self, src_path, dest_path):
        self.src_path = Path(src_path)
        self.dest_path = Path(dest_path)
        self.timestamp = datetime.now()
    
    def undo(self):
        """Reverse the file operation by moving the file back"""
        if self.dest_path.exists():
            self.src_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(self.dest_path), str(self.src_path))
            return True
        return False
    
    def to_dict(self):
        """Convert operation to dictionary for serialization"""
        return {
            'src_path': str(self.src_path),
            'dest_path': str(self.dest_path),
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create operation instance from dictionary"""
        operation = cls(data['src_path'], data['dest_path'])
        operation.timestamp = datetime.fromisoformat(data['timestamp'])
        return operation

class FileOrganizer:
    def __init__(self, source_dir):
        self.source_dir = Path(source_dir)
        self.setup_logging()
        
        # Define category mappings
        self.category_mappings = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xlsx', '.csv'],
            'audio': ['.mp3', '.wav', '.flac', '.m4a', '.aac'],
            'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.php']
        }
        
        # Custom rules storage
        self.custom_rules = []
        
        # Operation history
        self.operations = []
        self.history_file = self.source_dir / '.file_organizer_history.json'
        self.load_history()

    def setup_logging(self):
        """Configure logging to track file operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            handlers=[
                logging.FileHandler(f'file_organizer_{datetime.now():%Y%m%d_%H%M%S}.log'),
                logging.StreamHandler()
            ]
        )

    def save_history(self):
        """Save operation history to JSON file"""
        history_data = [op.to_dict() for op in self.operations]
        with open(self.history_file, 'w') as f:
            json.dump(history_data, f, indent=4)

    def load_history(self):
        """Load operation history from JSON file"""
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    history_data = json.load(f)
                self.operations = [FileOperation.from_dict(data) for data in history_data]
                logging.info(f"Loaded {len(self.operations)} historical operations")
            except Exception as e:
                logging.error(f"Error loading history: {e}")
                self.operations = []
        else:
            self.operations = []

    def undo_last(self):
        """Undo the last file operation"""
        if not self.operations:
            logging.info("No operations to undo")
            return False
        
        last_operation = self.operations.pop()
        if last_operation.undo():
            logging.info(f"Undid move of {last_operation.dest_path.name} back to {last_operation.src_path}")
            self.save_history()
            return True
        else:
            logging.error(f"Failed to undo move of {last_operation.dest_path.name}")
            return False

    def undo_all(self):
        """Undo all file operations in reverse order"""
        success_count = 0
        total_operations = len(self.operations)
        
        while self.operations:
            if self.undo_last():
                success_count += 1
        
        logging.info(f"Undid {success_count} out of {total_operations} operations")
        return success_count

    def get_operation_history(self):
        """Return formatted operation history"""
        history = []
        for op in self.operations:
            history.append({
                'timestamp': op.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'file': op.src_path.name,
                'from': str(op.src_path.parent),
                'to': str(op.dest_path.parent)
            })
        return history

    def add_custom_rule(self, pattern, destination):
        """Add a custom rule for file organization based on regex pattern"""
        try:
            compiled_pattern = re.compile(pattern)
            self.custom_rules.append((compiled_pattern, destination))
            logging.info(f"Added custom rule: {pattern} → {destination}")
        except re.error as e:
            logging.error(f"Invalid regex pattern: {str(e)}")

    def get_category(self, file_extension):
        """Determine the category of a file based on its extension"""
        # First check custom rules
        for pattern, destination in self.custom_rules:
            if pattern.match(file_extension.lower()):
                return destination
        
        # Then check standard categories
        for category, extensions in self.category_mappings.items():
            if file_extension.lower() in extensions:
                return category
        return 'misc'

    def create_category_dirs(self):
        """Create directories for each category if they don't exist"""
        # Create standard category directories
        for category in self.category_mappings.keys():
            category_path = self.source_dir / category
            category_path.mkdir(exist_ok=True)
            logging.info(f"Created/verified category directory: {category}")
        
        # Create directories for custom rules
        for _, destination in self.custom_rules:
            custom_path = self.source_dir / destination
            custom_path.mkdir(exist_ok=True)
            logging.info(f"Created/verified custom rule directory: {destination}")
        
        # Create misc directory for uncategorized files
        misc_path = self.source_dir / 'misc'
        misc_path.mkdir(exist_ok=True)
        logging.info("Created/verified misc directory")

    def organize_files(self, method='extension'):
        """Organize files using specified method"""
        self.create_category_dirs()
        moved_files = 0
        
        try:
            for item in self.source_dir.iterdir():
                if item.is_file() and item.name != '.file_organizer_history.json':
                    category = self.get_category(item.suffix)
                    dest_dir = self.source_dir / category
                    dest_path = dest_dir / item.name
                    
                    # Handle duplicates
                    if dest_path.exists():
                        base_name = dest_path.stem
                        extension = dest_path.suffix
                        counter = 1
                        
                        while dest_path.exists():
                            new_name = f"{base_name}_{counter}{extension}"
                            dest_path = dest_dir / new_name
                            counter += 1
                    
                    # Move file and record operation
                    shutil.move(str(item), str(dest_path))
                    self.operations.append(FileOperation(item, dest_path))
                    moved_files += 1
                    logging.info(f"Moved '{item.name}' to {category} directory")
                    
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            
        self.save_history()
        logging.info(f"Organization complete. Moved {moved_files} files.")
        return moved_files

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
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ")
        
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
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()