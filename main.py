import os
import shutil
from pathlib import Path
import logging
from datetime import datetime
import json
from collections import defaultdict
import re

class FileOperation:
    def __init__(self, src_path, dest_path, created_dir=None):
        self.src_path = Path(src_path)
        self.dest_path = Path(dest_path)
        self.created_dir = Path(created_dir) if created_dir else None
        self.timestamp = datetime.now()
    
        
    def undo(self):
        """Reverse the file operation and cleanup empty directories"""
        try:
            if self.dest_path.exists():
                # Create parent directory of source if it doesn't exist
                self.src_path.parent.mkdir(parents=True, exist_ok=True)
                # Move file back
                shutil.move(str(self.dest_path), str(self.src_path))
                
                # Try to remove the destination directory if it's empty
                dest_dir = self.dest_path.parent
                try:
                    if dest_dir.exists() and not any(dest_dir.iterdir()):
                        dest_dir.rmdir()
                        logging.info(f"Removed empty directory: {dest_dir}")
                except Exception as e:
                    logging.error(f"Error removing directory {dest_dir}: {e}")
                
                return True
            return False
        except Exception as e:
            logging.error(f"Error during undo: {e}")
            return False
    
    def to_dict(self):
        """Convert operation to dictionary for serialization"""
        return {
            'src_path': str(self.src_path),
            'dest_path': str(self.dest_path),
            'created_dir': str(self.created_dir) if self.created_dir else None,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create operation instance from dictionary"""
        operation = cls(
            data['src_path'], 
            data['dest_path'],
            data['created_dir']
        )
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
        log_filename = f'file_organizer_{datetime.now():%Y%m%d_%H%M%S}.log'
        log_file = Path(self.source_dir) / log_filename
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()  # This will also print to console
            ]
        )
        
        logging.info(f"Started file organization in: {self.source_dir}")
        logging.info(f"Log file created at: {log_file}")

    def analyze_directory(self):
        """Analyze directory and return required categories"""
        required_categories = set()
        for item in self.source_dir.iterdir():
            if item.is_file() and item.name != '.file_organizer_history.json':
                category = self.get_category(item.suffix)
                required_categories.add(category)
        return required_categories

    def create_category_dir(self, category):
        """Create a single category directory and return True if created"""
        category_path = self.source_dir / category
        if not category_path.exists():
            category_path.mkdir(exist_ok=True)
            logging.info(f"Created category directory: {category}")
            return True
        return False

    def cleanup_empty_directories(self):
        """Remove empty category directories"""
        removed = []
        for category in self.category_mappings.keys():
            category_path = self.source_dir / category
            try:
                if category_path.exists() and not any(category_path.iterdir()):
                    category_path.rmdir()
                    removed.append(category)
                    logging.info(f"Removed empty directory: {category}")
            except Exception as e:
                logging.error(f"Error removing directory {category}: {e}")
        
        # Also check misc directory
        misc_path = self.source_dir / 'misc'
        if misc_path.exists() and not any(misc_path.iterdir()):
            try:
                misc_path.rmdir()
                removed.append('misc')
                logging.info("Removed empty misc directory")
            except Exception as e:
                logging.error(f"Error removing misc directory: {e}")
        
        return removed

    def organize_files(self, method='extension'):
        """Organize files using specified method"""
        # Analyze directory first
        required_categories = self.analyze_directory()
        
        # Create only needed directories
        created_dirs = set()
        for category in required_categories:
            if self.create_category_dir(category):
                created_dirs.add(category)
        
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
                    created_dir = category if category in created_dirs else None
                    self.operations.append(FileOperation(item, dest_path, created_dir))
                    moved_files += 1
                    logging.info(f"Moved '{item.name}' to {category} directory")
                    
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            
        self.save_history()
        logging.info(f"Organization complete. Moved {moved_files} files.")
        return moved_files

    def undo_last(self):
        """Undo the last file operation"""
        if not self.operations:
            logging.info("No operations to undo")
            return False
        
        last_operation = self.operations.pop()
        if last_operation.undo():
            logging.info(f"Undid move of {last_operation.dest_path.name} back to {last_operation.src_path}")
            self.save_history()
            self.cleanup_empty_directories()
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
        
        # Final cleanup of any remaining empty directories
        self.cleanup_empty_directories()
        
        logging.info(f"Undid {success_count} out of {total_operations} operations")
        return success_count

    
    def get_category(self, file_extension):
        """
        Determine the category of a file based on its extension and custom rules.
        
        Args:
            file_extension (str): The file extension including the dot (e.g., '.txt')
        
        Returns:
            str: The category name the file belongs to
        """
        # First check custom rules
        for pattern, destination in self.custom_rules:
            if pattern.match(file_extension.lower()):
                logging.debug(f"Matched custom rule: {file_extension} → {destination}")
                return destination
        
        # Then check standard categories
        for category, extensions in self.category_mappings.items():
            if file_extension.lower() in extensions:
                logging.debug(f"Matched category {category} for extension {file_extension}")
                return category
        
        # If no match found, return misc
        logging.debug(f"No category match for {file_extension}, using 'misc'")
        return 'misc'

    def add_extension_category(self, category, extensions):
        """
        Add new extensions to an existing or new category.
        
        Args:
            category (str): The category name
            extensions (list): List of file extensions including the dot
        """
        if category not in self.category_mappings:
            self.category_mappings[category] = []
            logging.info(f"Created new category: {category}")
        
        # Add new extensions, avoiding duplicates
        added = []
        for ext in extensions:
            ext = ext.lower()
            if ext not in self.category_mappings[category]:
                self.category_mappings[category].append(ext)
                added.append(ext)
        
        if added:
            logging.info(f"Added extensions to {category}: {', '.join(added)}")
        else:
            logging.info(f"No new extensions added to {category}")

    def get_category_stats(self):
        """
        Get statistics about categories and their extensions.
        
        Returns:
            dict: Statistics about categories and extensions
        """
        stats = {
            'total_categories': len(self.category_mappings),
            'total_extensions': sum(len(exts) for exts in self.category_mappings.values()),
            'categories': {}
        }
        
        for category, extensions in self.category_mappings.items():
            stats['categories'][category] = {
                'extension_count': len(extensions),
                'extensions': sorted(extensions)
            }
        
        # Add custom rules info
        stats['custom_rules'] = len(self.custom_rules)
        
        return stats

    def remove_extension(self, extension, category=None):
        """
        Remove an extension from a category or all categories.
        
        Args:
            extension (str): The extension to remove
            category (str, optional): Specific category to remove from. If None, removes from all.
        
        Returns:
            bool: True if extension was removed, False otherwise
        """
        extension = extension.lower()
        removed = False
        
        if category:
            if category in self.category_mappings and extension in self.category_mappings[category]:
                self.category_mappings[category].remove(extension)
                logging.info(f"Removed {extension} from {category}")
                removed = True
        else:
            for cat, extensions in self.category_mappings.items():
                if extension in extensions:
                    extensions.remove(extension)
                    logging.info(f"Removed {extension} from {cat}")
                    removed = True
        
        return removed
    def save_history(self):
        """Save operation history to JSON file"""
        history_data = [op.to_dict() for op in self.operations]
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history_data, f, indent=4)
            logging.info(f"Saved {len(history_data)} operations to history file")
        except Exception as e:
            logging.error(f"Error saving history: {e}")

    def load_history(self):
        """Load operation history from JSON file"""
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    history_data = json.load(f)
                
                self.operations = []
                for data in history_data:
                    try:
                        operation = FileOperation.from_dict(data)
                        self.operations.append(operation)
                    except Exception as e:
                        logging.error(f"Error loading operation: {e}")
                
                logging.info(f"Loaded {len(self.operations)} historical operations")
            except Exception as e:
                logging.error(f"Error loading history file: {e}")
                self.operations = []
        else:
            logging.info("No history file found, starting fresh")
            self.operations = []

    def get_operation_history(self):
        """Return formatted operation history"""
        history = []
        for op in self.operations:
            history.append({
                'timestamp': op.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'file': op.src_path.name,
                'from': str(op.src_path.parent),
                'to': str(op.dest_path.parent),
                'created_dir': str(op.created_dir) if op.created_dir else None
            })
        return history

    def clear_history(self):
        """Clear operation history and remove history file"""
        self.operations = []
        try:
            if self.history_file.exists():
                self.history_file.unlink()
                logging.info("History file removed")
        except Exception as e:
            logging.error(f"Error removing history file: {e}")

    def get_history_stats(self):
        """Get statistics about the operation history"""
        if not self.operations:
            return "No operations in history"
        
        stats = {
            'total_operations': len(self.operations),
            'first_operation': self.operations[0].timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'last_operation': self.operations[-1].timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'categories_affected': set(),
            'directories_created': set()
        }
        
        for op in self.operations:
            stats['categories_affected'].add(op.dest_path.parent.name)
            if op.created_dir:
                stats['directories_created'].add(str(op.created_dir))
        
        return stats

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

if __name__ == "__main__":
    main()