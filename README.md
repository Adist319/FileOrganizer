# File Directory Organizer

A Python utility that automatically organizes files into categorical directories based on their extensions. Features smart directory management, undo functionality, and detailed operation logging.

## Features

### Core Functionality
- Organizes files by type into appropriate directories
- Creates directories only when needed (no empty folders)
- Handles file naming conflicts automatically
- Maintains original file names with numeric suffixes for duplicates

### Smart Category Management
- Pre-configured categories for common file types:
  - Images (.jpg, .jpeg, .png, .gif, etc.)
  - Documents (.pdf, .doc, .docx, .txt, etc.)
  - Audio (.mp3, .wav, .flac, etc.)
  - Video (.mp4, .avi, .mkv, etc.)
  - Archives (.zip, .rar, .7z, etc.)
  - Code (.py, .js, .html, etc.)
- Custom rule support using regex patterns
- Miscellaneous category for unmatched files

### Undo Functionality
- Undo last operation
- Undo all operations
- Automatic cleanup of empty directories
- Persistent operation history
- Detailed operation logging

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/file-organizer.git
cd file-organizer
```

2. No external dependencies required - uses Python standard library only!

## Project Structure
```
file-organizer/
├── file_organizer.py     # Core classes and functionality
├── main.py              # Command-line interface
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Usage

### Basic Usage
```python
from file_organizer import FileOrganizer

# Initialize organizer
organizer = FileOrganizer("/path/to/directory")

# Organize files
organizer.organize_files()
```

### Command Line Interface
Run the program:
```bash
python main.py
```

The interactive menu provides options to:
1. Organize files
2. Undo last operation
3. Undo all operations
4. Show operation history
5. Add custom rules
6. Cleanup empty directories
7. Exit

### Adding Custom Rules
```python
organizer = FileOrganizer("/path/to/directory")
organizer.add_custom_rule(r'\.log$', 'logs')  # Move all .log files to 'logs' directory
```

### Managing Categories
```python
# Add new category
organizer.add_extension_category('ebooks', ['.epub', '.mobi', '.azw3'])

# Get category for a file
category = organizer.get_category('.pdf')
```

## Features in Detail

### Operation Logging
- Creates timestamped log files
- Logs all file operations
- Tracks directory creation and removal
- Maintains operation history for undo functionality

### Smart Directory Management
- Only creates directories that will be used
- Automatically removes empty directories after undo
- Prevents directory clutter
- Handles nested directories properly

### History Management
- Saves operation history to JSON
- Persists between sessions
- Allows for operation auditing
- Supports undo functionality

## Example Workflow

```python
from file_organizer import FileOrganizer

# Initialize
organizer = FileOrganizer("~/Downloads")

# Add custom rule for project files
organizer.add_custom_rule(r'\.project$', 'projects')

# Organize files
organizer.organize_files()

# Oops! Undo last operation if needed
organizer.undo_last()

# View operation history
history = organizer.get_operation_history()
for entry in history:
    print(f"Moved {entry['file']} to {entry['to']}")
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Maintain Python standard library independence
- Add tests for new features
- Update documentation
- Follow PEP 8 style guidelines

## Future Development Plans

- More supported file types
- GUI interface
- Advanced file type detection
- Content-based organization
- Multi-threading support
- Scheduled organization
- File type previews
- Organization templates

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Support

For support, please open an issue in the GitHub repository.