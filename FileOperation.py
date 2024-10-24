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