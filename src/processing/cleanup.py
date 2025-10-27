"""Cleanup utilities for processed files."""
import os
from ..utils.helpers import delete_file_safe, delete_directory_safe
from ..error_handling.logger import logger


class CleanupManager:
    """Manages cleanup of temporary and processed files."""
    
    def __init__(self, storage, config):
        self.storage = storage
        self.config = config
        self.auto_delete = config.get('storage.auto_delete_raw', True)
    
    def cleanup_session_files(self, session_id, recordings):
        """Clean up files from a specific session."""
        if not self.auto_delete:
            logger.info("Auto-delete disabled, keeping raw files")
            return
        
        try:
            deleted_count = 0
            
            # Delete recording files
            for recording in recordings:
                if os.path.exists(recording):
                    if delete_file_safe(recording):
                        deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} files from session {session_id}")
        except Exception as e:
            logger.error(f"Error cleaning up session files: {e}")
    
    def cleanup_temp_directory(self):
        """Clean up entire temp directory."""
        try:
            temp_path = self.storage.temp_path
            if os.path.exists(temp_path):
                # Delete all files in temp
                for filename in os.listdir(temp_path):
                    filepath = os.path.join(temp_path, filename)
                    if os.path.isfile(filepath):
                        delete_file_safe(filepath)
            
            logger.info("Cleaned up temp directory")
        except Exception as e:
            logger.error(f"Error cleaning up temp directory: {e}")
    
    def cleanup_old_processed_files(self, max_age_days=30):
        """Delete processed files older than specified days."""
        try:
            import time
            processed_path = self.storage.processed_path
            current_time = time.time()
            deleted_count = 0
            
            for filename in os.listdir(processed_path):
                filepath = os.path.join(processed_path, filename)
                if os.path.isfile(filepath):
                    file_age_days = (current_time - os.path.getmtime(filepath)) / (24 * 3600)
                    if file_age_days > max_age_days:
                        if delete_file_safe(filepath):
                            deleted_count += 1
            
            logger.info(f"Deleted {deleted_count} old processed files")
        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")
