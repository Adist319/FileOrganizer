import os
import shutil
from pathlib import Path
import logging
from datetime import datetime

class FileOrganizer:
    def __init__(self, source_dir):
        self.source_dir = Path(source_dir)
        self.setup_logging()
        
        # Define category mappings
        self.category_mappings = {
            # Images
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
            # Documents
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xlsx', '.csv'],
            # Audio
            'audio': ['.mp3', '.wav', '.flac', '.m4a', '.aac'],
            # Video
            'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
            # Archives
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            # Code
            'code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.php']
        }

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

    def get_category(self, file_extension):
        """Determine the category of a file based on its extension"""
        for category, extensions in self.category_mappings.items():
            if file_extension.lower() in extensions:
                return category
        return 'misc'

    def create_category_dirs(self):
        """Create directories for each category if they don't exist"""
        for category in self.category_mappings.keys():
            category_path = self.source_dir / category
            category_path.mkdir(exist_ok=True)
        
        # Create misc directory for uncategorized files
        (self.source_dir / 'misc').mkdir(exist_ok=True)

    def organize_files(self):
        """Organize files into appropriate directories based on their extensions"""
        self.create_category_dirs()
        
        # Counter for moved files
        moved_files = 0
        
        try:
            for item in self.source_dir.iterdir():
                if item.is_file():  # Skip directories
                    # Get file extension and category
                    file_extension = item.suffix
                    category = self.get_category(file_extension)
                    
                    # Define destination path
                    dest_dir = self.source_dir / category
                    dest_path = dest_dir / item.name
                    
                    # Handle duplicate files
                    if dest_path.exists():
                        base_name = dest_path.stem
                        extension = dest_path.suffix
                        counter = 1
                        
                        while dest_path.exists():
                            new_name = f"{base_name}_{counter}{extension}"
                            dest_path = dest_dir / new_name
                            counter += 1
                    
                    try:
                        # Move the file
                        shutil.move(str(item), str(dest_path))
                        moved_files += 1
                        logging.info(f"Moved '{item.name}' to {category} directory")
                    except Exception as e:
                        logging.error(f"Error moving '{item.name}': {str(e)}")
                        
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            
        logging.info(f"Organization complete. Moved {moved_files} files.")
        return moved_files

def main():
    # Get the directory to organize from user input
    directory = input("Enter the directory path to organize: ")
    
    # Verify the directory exists
    if not os.path.isdir(directory):
        print("Error: Invalid directory path")
        return
    
    # Create and run organizer
    organizer = FileOrganizer(directory)
    files_moved = organizer.organize_files()
    
    print(f"\nOrganization complete! Moved {files_moved} files.")
    print("Check the log file for detailed information about the operations performed.")

if __name__ == "__main__":
    main()