import os
import shutil
from pathlib import Path
import logging
from datetime import datetime
import time
from collections import defaultdict
import re

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
        
        # Size categories (in bytes)
        self.size_categories = {
            'tiny': (0, 1024 * 100),  # 0 - 100KB
            'small': (1024 * 100, 1024 * 1024),  # 100KB - 1MB
            'medium': (1024 * 1024, 1024 * 1024 * 50),  # 1MB - 50MB
            'large': (1024 * 1024 * 50, 1024 * 1024 * 1024),  # 50MB - 1GB
            'huge': (1024 * 1024 * 1024, float('inf'))  # > 1GB
        }
        
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

    def add_custom_rule(self, pattern, destination):
        """Add a custom rule for file organization based on regex pattern"""
        try:
            compiled_pattern = re.compile(pattern)
            self.custom_rules.append((compiled_pattern, destination))
            logging.info(f"Added custom rule: {pattern} → {destination}")
        except re.error as e:
            logging.error(f"Invalid regex pattern: {str(e)}")

    def add_extension_category(self, category, extensions):
        """Add new file extensions to existing or new category"""
        if category not in self.category_mappings:
            self.category_mappings[category] = []
        self.category_mappings[category].extend(extensions)
        logging.info(f"Added extensions {extensions} to category {category}")

    def organize_by_date(self, date_format='%Y/%m'):
        """Organize files into directories based on creation date"""
        for item in self.source_dir.iterdir():
            if item.is_file():
                try:
                    # Get file creation time
                    creation_time = datetime.fromtimestamp(item.stat().st_ctime)
                    # Create date-based directory
                    date_dir = self.source_dir / creation_time.strftime(date_format)
                    date_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Move file
                    shutil.move(str(item), str(date_dir / item.name))
                    logging.info(f"Moved '{item.name}' to {date_dir}")
                except Exception as e:
                    logging.error(f"Error organizing '{item.name}' by date: {str(e)}")

    def organize_by_size(self):
        """Organize files into directories based on file size"""
        for item in self.source_dir.iterdir():
            if item.is_file():
                try:
                    file_size = item.stat().st_size
                    # Determine size category
                    for category, (min_size, max_size) in self.size_categories.items():
                        if min_size <= file_size < max_size:
                            size_dir = self.source_dir / f'size_{category}'
                            size_dir.mkdir(exist_ok=True)
                            shutil.move(str(item), str(size_dir / item.name))
                            logging.info(f"Moved '{item.name}' to {size_dir}")
                            break
                except Exception as e:
                    logging.error(f"Error organizing '{item.name}' by size: {str(e)}")

    def analyze_directory(self):
        """Analyze directory contents and return statistics"""
        stats = {
            'total_files': 0,
            'total_size': 0,
            'extensions': defaultdict(int),
            'categories': defaultdict(int),
            'size_distribution': defaultdict(int)
        }
        
        for item in self.source_dir.rglob('*'):
            if item.is_file():
                stats['total_files'] += 1
                file_size = item.stat().st_size
                stats['total_size'] += file_size
                stats['extensions'][item.suffix.lower()] += 1
                
                # Categorize by size
                for size_cat, (min_size, max_size) in self.size_categories.items():
                    if min_size <= file_size < max_size:
                        stats['size_distribution'][size_cat] += 1
                        break
                
                # Categorize by type
                category = self.get_category(item.suffix)
                stats['categories'][category] += 1
        
        return stats

    def get_category(self, file_extension):
        """Determine the category of a file based on its extension and custom rules"""
        # First check custom rules
        for pattern, destination in self.custom_rules:
            if pattern.match(file_extension.lower()):
                return destination
        
        # Then check standard categories
        for category, extensions in self.category_mappings.items():
            if file_extension.lower() in extensions:
                return category
        return 'misc'

    def organize_files(self, method='extension'):
        """
        Organize files using specified method:
        - 'extension': organize by file type
        - 'date': organize by creation date
        - 'size': organize by file size
        """
        if method == 'extension':
            self.create_category_dirs()
            moved_files = self._organize_by_extension()
        elif method == 'date':
            moved_files = self.organize_by_date()
        elif method == 'size':
            moved_files = self.organize_by_size()
        else:
            logging.error(f"Unknown organization method: {method}")
            return 0
            
        logging.info(f"Organization complete. Moved {moved_files} files.")
        return moved_files

    def _organize_by_extension(self):
        """Internal method for organizing by extension"""
        moved_files = 0
        
        try:
            for item in self.source_dir.iterdir():
                if item.is_file():
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
                    
                    # Move file
                    shutil.move(str(item), str(dest_path))
                    moved_files += 1
                    logging.info(f"Moved '{item.name}' to {category} directory")
                    
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            
        return moved_files

def main():
    # Example usage of extended functionality
    directory = input("Enter the directory path to organize: ")
    
    if not os.path.isdir(directory):
        print("Error: Invalid directory path")
        return
    
    organizer = FileOrganizer(directory)
    
    # Add custom rules example
    organizer.add_custom_rule(r'\.log$', 'logs')
    organizer.add_custom_rule(r'backup.*\.', 'backups')
    
    # Add new category example
    organizer.add_extension_category('ebooks', ['.epub', '.mobi', '.azw3'])
    
    # Analyze directory before organizing
    print("\nAnalyzing directory...")
    stats = organizer.analyze_directory()
    print(f"Total files: {stats['total_files']}")
    print(f"Total size: {stats['total_size'] / (1024*1024):.2f} MB")
    print("\nFile type distribution:")
    for ext, count in stats['extensions'].items():
        print(f"{ext}: {count} files")
    
    # Choose organization method
    print("\nOrganization methods:")
    print("1. By extension")
    print("2. By date")
    print("3. By size")
    choice = input("Choose organization method (1-3): ")
    
    method_map = {'1': 'extension', '2': 'date', '3': 'size'}
    if choice in method_map:
        files_moved = organizer.organize_files(method_map[choice])
        print(f"\nOrganization complete! Moved {files_moved} files.")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()