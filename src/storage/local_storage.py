"""Local storage management."""
import os
import shutil
from pathlib import Path
from ..utils.helpers import (
    ensure_directory, 
    get_directory_size_gb,
    delete_file_safe
)
from ..utils.validators import validate_directory_writable, validate_disk_space
from ..error_handling.exceptions import StorageError
from ..error_handling.logger import logger


class LocalStorage:
    """Manages local file storage."""
    
    def __init__(self, config):
        self.config = config
        self.base_path = config.get('storage.local_path', './user_data')
        self.temp_path = config.get('storage.temp_path', './user_data/temp')
        self.recordings_path = config.get('storage.recordings_path', './user_data/recordings')
        self.processed_path = config.get('storage.processed_path', './user_data/processed')
        self.max_storage_gb = config.get('storage.max_storage_gb', 5)
        
        self._initialize_directories()
    
    def _initialize_directories(self):
        """Initialize all required directories."""
        try:
            ensure_directory(self.base_path)
            ensure_directory(self.temp_path)
            ensure_directory(self.recordings_path)
            ensure_directory(self.processed_path)
            logger.info("Storage directories initialized")
        except Exception as e:
            raise StorageError(f"Failed to initialize directories: {e}")
    
    def check_disk_space(self, required_gb=1):
        """Check if sufficient disk space is available."""
        return validate_disk_space(self.base_path, required_gb)
    
    def check_storage_quota(self):
        """Check if storage quota is exceeded."""
        current_size = get_directory_size_gb(self.base_path)
        return current_size < self.max_storage_gb
    
    def get_temp_file_path(self, filename):
        """Get path for temporary file."""
        return os.path.join(self.temp_path, filename)
    
    def get_recording_file_path(self, filename):
        """Get path for recording file."""
        return os.path.join(self.recordings_path, filename)
    
    def get_processed_file_path(self, filename):
        """Get path for processed file."""
        return os.path.join(self.processed_path, filename)
    
    def cleanup_temp_files(self):
        """Clean up temporary files."""
        try:
            if os.path.exists(self.temp_path):
                shutil.rmtree(self.temp_path)
                ensure_directory(self.temp_path)
            logger.info("Temporary files cleaned up")
        except Exception as e:
            logger.error(f"Failed to cleanup temp files: {e}")
    
    def delete_old_recordings(self, max_count=10):
        """Delete old recordings to free space."""
        try:
            files = []
            for filename in os.listdir(self.recordings_path):
                filepath = os.path.join(self.recordings_path, filename)
                if os.path.isfile(filepath):
                    files.append((filepath, os.path.getmtime(filepath)))
            
            # Sort by modification time
            files.sort(key=lambda x: x[1])
            
            # Delete oldest files if exceeding max_count
            if len(files) > max_count:
                for filepath, _ in files[:len(files) - max_count]:
                    delete_file_safe(filepath)
                logger.info(f"Deleted {len(files) - max_count} old recordings")
        except Exception as e:
            logger.error(f"Failed to delete old recordings: {e}")
