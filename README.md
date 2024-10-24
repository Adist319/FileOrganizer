# File Directory Organizer

A Python-based utility for automatically organizing files in directories based on various criteria like file type, date, or size. Perfect for cleaning up downloads folders, organizing media collections, or maintaining organized project directories.

## Features

- **Multiple Organization Methods**
  - By file extension (images, documents, audio, etc.)
  - By creation date (YYYY/MM structure)
  - By file size (tiny to huge)

- **Smart Categorization**
  - Pre-configured categories for common file types
  - Custom rule support using regex patterns
  - Miscellaneous category for unmatched files

- **Safe Operations**
  - Duplicate file handling
  - Operation logging
  - Maintains original files' names

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/file-organizer.git
cd file-organizer
```

2. No additional dependencies required - uses Python standard library only!

## Quick Start

```python
from file_organizer import FileOrganizer

# Initialize organizer with target directory
organizer = FileOrganizer("/path/to/directory")

# Add any custom rules (optional)
organizer.add_custom_rule(r'\.log$', 'logs')

# Organize files
organizer.organize_files()
```

Or use from command line:
```bash
python main.py
```

## Default Categories

- **Images**: .jpg, .jpeg, .png, .gif, .bmp, .tiff, .webp
- **Documents**: .pdf, .doc, .docx, .txt, .rtf, .odt, .xlsx, .csv
- **Audio**: .mp3, .wav, .flac, .m4a, .aac
- **Video**: .mp4, .avi, .mkv, .mov, .wmv
- **Archives**: .zip, .rar, .7z, .tar, .gz
- **Code**: .py, .js, .html, .css, .java, .cpp, .php

## Adding Custom Categories

```python
organizer = FileOrganizer("/path/to/directory")
organizer.add_extension_category('ebooks', ['.epub', '.mobi', '.azw3'])
```

## Size Categories

- Tiny: 0 - 100KB
- Small: 100KB - 1MB
- Medium: 1MB - 50MB
- Large: 50MB - 1GB
- Huge: > 1GB

## Logging

The script generates detailed logs of all operations in the format:
`file_organizer_YYYYMMDD_HHMMSS.log`

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Future Development Plans

- More supported file categories
- GUI interface
- Real-time file monitoring
- Advanced duplicate detection
- Content-based organization
- Multi-threading support for large directories

## Support

For support, please open an issue in the GitHub repository.
