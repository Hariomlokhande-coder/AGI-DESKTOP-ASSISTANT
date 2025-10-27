"""Enhanced utility helper functions with comprehensive error handling and edge case management."""

import os
import json
import shutil
import hashlib
import mimetypes
import tempfile
import zipfile
import tarfile
import gzip
import bz2
import time
import threading
import queue
import subprocess
import platform
import psutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from collections import deque
import logging

from .constants import (
    StorageConstants, FileFormatConstants, 
    validate_filename, validate_storage_path
)
from ..error_handling.exceptions import (
    StorageError, ValidationError, ResourceError,
    handle_exception
)

# Initialize logger
logger = logging.getLogger(__name__)

# Global cache for performance
_file_cache = {}
_cache_lock = threading.Lock()
_cache_max_size = 1000
_cache_ttl = 3600  # 1 hour

class FileCache:
    """Enhanced file cache with TTL and size limits."""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache = {}
        self.access_times = {}
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        with self.lock:
            if key in self.cache:
                # Check TTL
                if time.time() - self.access_times[key] > self.ttl:
                    del self.cache[key]
                    del self.access_times[key]
                    return None
                
                self.access_times[key] = time.time()
                return self.cache[key]
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Set item in cache."""
        with self.lock:
            # Remove oldest items if cache is full
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.access_times.keys(), key=self.access_times.get)
                del self.cache[oldest_key]
                del self.access_times[oldest_key]
            
            self.cache[key] = value
            self.access_times[key] = time.time()
    
    def clear(self) -> None:
        """Clear cache."""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
    
    def size(self) -> int:
        """Get cache size."""
        with self.lock:
            return len(self.cache)

# Global file cache instance
file_cache = FileCache()

def get_timestamp(format_string: str = "%Y%m%d_%H%M%S") -> str:
    """Get current timestamp string with customizable format."""
    try:
        return datetime.now().strftime(format_string)
    except Exception as e:
        logger.error(f"Error generating timestamp: {e}")
        return datetime.now().strftime("%Y%m%d_%H%M%S")

def get_utc_timestamp() -> str:
    """Get current UTC timestamp."""
    try:
        return datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    except Exception as e:
        logger.error(f"Error generating UTC timestamp: {e}")
        return datetime.utcnow().strftime("%Y%m%d_%H%M%S")

def ensure_directory(path: Union[str, Path], permissions: int = 0o755) -> Path:
    """Ensure directory exists with comprehensive error handling."""
    try:
        path_obj = Path(path)
        
        # Validate path
        if not validate_storage_path(str(path_obj)):
            raise ValidationError(f"Invalid directory path: {path}")
        
        # Create directory if it doesn't exist
        if not path_obj.exists():
            path_obj.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {path_obj}")
        
        # Set permissions if specified
        if permissions:
            os.chmod(path_obj, permissions)
        
        return path_obj
        
    except Exception as e:
        logger.error(f"Error ensuring directory {path}: {e}")
        raise StorageError(f"Failed to ensure directory {path}: {e}")

def ensure_file_directory(filepath: Union[str, Path]) -> Path:
    """Ensure parent directory of file exists."""
    try:
        file_path = Path(filepath)
        parent_dir = file_path.parent
        return ensure_directory(parent_dir)
    except Exception as e:
        logger.error(f"Error ensuring file directory {filepath}: {e}")
        raise StorageError(f"Failed to ensure file directory {filepath}: {e}")

def get_file_size_mb(filepath: Union[str, Path]) -> float:
    """Get file size in MB with comprehensive error handling."""
    try:
        file_path = Path(filepath)
        
        if not file_path.exists():
            logger.warning(f"File does not exist: {file_path}")
            return 0.0
        
        if not file_path.is_file():
            logger.warning(f"Path is not a file: {file_path}")
            return 0.0
        
        size_bytes = file_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        
        logger.debug(f"File size: {file_path} = {size_mb:.2f} MB")
        return size_mb
        
    except Exception as e:
        logger.error(f"Error getting file size {filepath}: {e}")
        return 0.0

def get_file_size_gb(filepath: Union[str, Path]) -> float:
    """Get file size in GB."""
    try:
        size_mb = get_file_size_mb(filepath)
        return size_mb / 1024
    except Exception as e:
        logger.error(f"Error getting file size in GB {filepath}: {e}")
        return 0.0

def get_directory_size_gb(directory: Union[str, Path]) -> float:
    """Get total size of directory in GB with comprehensive error handling."""
    try:
        dir_path = Path(directory)
        
        if not dir_path.exists():
            logger.warning(f"Directory does not exist: {dir_path}")
            return 0.0
        
        if not dir_path.is_dir():
            logger.warning(f"Path is not a directory: {dir_path}")
            return 0.0
        
        total_size = 0
        file_count = 0
        
        for file_path in dir_path.rglob('*'):
            try:
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1
                    
                    # Log progress for large directories
                    if file_count % 1000 == 0:
                        logger.debug(f"Processed {file_count} files in {dir_path}")
                        
            except (PermissionError, OSError) as e:
                logger.warning(f"Cannot access file {file_path}: {e}")
                continue
        
        size_gb = total_size / (1024 * 1024 * 1024)
        logger.info(f"Directory size: {dir_path} = {size_gb:.2f} GB ({file_count} files)")
        return size_gb
        
    except Exception as e:
        logger.error(f"Error getting directory size {directory}: {e}")
        return 0.0

def get_directory_size_mb(directory: Union[str, Path]) -> float:
    """Get total size of directory in MB."""
    try:
        size_gb = get_directory_size_gb(directory)
        return size_gb * 1024
    except Exception as e:
        logger.error(f"Error getting directory size in MB {directory}: {e}")
        return 0.0

def get_file_hash(filepath: Union[str, Path], algorithm: str = 'sha256') -> Optional[str]:
    """Get file hash with comprehensive error handling."""
    try:
        file_path = Path(filepath)
        
        if not file_path.exists():
            logger.warning(f"File does not exist: {file_path}")
            return None
        
        if not file_path.is_file():
            logger.warning(f"Path is not a file: {file_path}")
            return None
        
        # Check cache first
        cache_key = f"hash_{algorithm}_{file_path}_{file_path.stat().st_mtime}"
        cached_hash = file_cache.get(cache_key)
        if cached_hash:
            return cached_hash
        
        # Calculate hash
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(8192), b""):
                hash_obj.update(chunk)
        
        file_hash = hash_obj.hexdigest()
        
        # Cache the result
        file_cache.set(cache_key, file_hash)
        
        logger.debug(f"File hash ({algorithm}): {file_path} = {file_hash}")
        return file_hash
        
    except Exception as e:
        logger.error(f"Error calculating file hash {filepath}: {e}")
        return None

def get_file_mime_type(filepath: Union[str, Path]) -> Optional[str]:
    """Get file MIME type with comprehensive error handling."""
    try:
        file_path = Path(filepath)
        
        if not file_path.exists():
            logger.warning(f"File does not exist: {file_path}")
            return None
        
        if not file_path.is_file():
            logger.warning(f"Path is not a file: {file_path}")
            return None
        
        # Try to guess MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        
        if mime_type:
            logger.debug(f"File MIME type: {file_path} = {mime_type}")
            return mime_type
        else:
            logger.warning(f"Could not determine MIME type for: {file_path}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting MIME type {filepath}: {e}")
        return None

def save_json(data: Any, filepath: Union[str, Path], 
              indent: int = 2, ensure_ascii: bool = False,
              backup: bool = True) -> bool:
    """Save data to JSON file with comprehensive error handling."""
    try:
        file_path = Path(filepath)
        
        # Validate filename
        if not validate_filename(file_path.name):
            raise ValidationError(f"Invalid filename: {file_path.name}")
        
        # Ensure directory exists
        ensure_file_directory(file_path)
        
        # Create backup if file exists and backup is enabled
        if backup and file_path.exists():
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
            try:
                shutil.copy2(file_path, backup_path)
                logger.debug(f"Created backup: {backup_path}")
            except Exception as e:
                logger.warning(f"Failed to create backup: {e}")
        
        # Write to temporary file first
        temp_path = file_path.with_suffix(f"{file_path.suffix}.tmp")
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii, 
                     default=str)  # Handle non-serializable objects
        
        # Atomic move
        temp_path.replace(file_path)
        
        logger.info(f"Saved JSON data to: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving JSON {filepath}: {e}")
        # Clean up temporary file
        try:
            temp_path = Path(filepath).with_suffix(f"{Path(filepath).suffix}.tmp")
            if temp_path.exists():
                temp_path.unlink()
        except:
            pass
        raise StorageError(f"Failed to save JSON {filepath}: {e}")

def load_json(filepath: Union[str, Path], default: Any = None) -> Any:
    """Load data from JSON file with comprehensive error handling."""
    try:
        file_path = Path(filepath)
        
        if not file_path.exists():
            logger.warning(f"JSON file does not exist: {file_path}")
            return default
        
        if not file_path.is_file():
            logger.warning(f"Path is not a file: {file_path}")
            return default
        
        # Check cache first
        cache_key = f"json_{file_path}_{file_path.stat().st_mtime}"
        cached_data = file_cache.get(cache_key)
        if cached_data:
            return cached_data
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Cache the result
        file_cache.set(cache_key, data)
        
        logger.debug(f"Loaded JSON data from: {file_path}")
        return data
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error {filepath}: {e}")
        return default
    except Exception as e:
        logger.error(f"Error loading JSON {filepath}: {e}")
        return default

def save_yaml(data: Any, filepath: Union[str, Path], 
              backup: bool = True) -> bool:
    """Save data to YAML file with comprehensive error handling."""
    try:
        import yaml
        
        file_path = Path(filepath)
        
        # Validate filename
        if not validate_filename(file_path.name):
            raise ValidationError(f"Invalid filename: {file_path.name}")
        
        # Ensure directory exists
        ensure_file_directory(file_path)
        
        # Create backup if file exists and backup is enabled
        if backup and file_path.exists():
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
            try:
                shutil.copy2(file_path, backup_path)
                logger.debug(f"Created backup: {backup_path}")
            except Exception as e:
                logger.warning(f"Failed to create backup: {e}")
        
        # Write to temporary file first
        temp_path = file_path.with_suffix(f"{file_path.suffix}.tmp")
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        
        # Atomic move
        temp_path.replace(file_path)
        
        logger.info(f"Saved YAML data to: {file_path}")
        return True
        
    except ImportError:
        logger.error("PyYAML not installed, cannot save YAML file")
        raise DependencyError("PyYAML not installed")
    except Exception as e:
        logger.error(f"Error saving YAML {filepath}: {e}")
        # Clean up temporary file
        try:
            temp_path = Path(filepath).with_suffix(f"{Path(filepath).suffix}.tmp")
            if temp_path.exists():
                temp_path.unlink()
        except:
            pass
        raise StorageError(f"Failed to save YAML {filepath}: {e}")

def load_yaml(filepath: Union[str, Path], default: Any = None) -> Any:
    """Load data from YAML file with comprehensive error handling."""
    try:
        import yaml
        
        file_path = Path(filepath)
        
        if not file_path.exists():
            logger.warning(f"YAML file does not exist: {file_path}")
            return default
        
        if not file_path.is_file():
            logger.warning(f"Path is not a file: {file_path}")
            return default
        
        # Check cache first
        cache_key = f"yaml_{file_path}_{file_path.stat().st_mtime}"
        cached_data = file_cache.get(cache_key)
        if cached_data:
            return cached_data
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Cache the result
        file_cache.set(cache_key, data)
        
        logger.debug(f"Loaded YAML data from: {file_path}")
        return data
        
    except ImportError:
        logger.error("PyYAML not installed, cannot load YAML file")
        return default
    except yaml.YAMLError as e:
        logger.error(f"YAML parse error {filepath}: {e}")
        return default
    except Exception as e:
        logger.error(f"Error loading YAML {filepath}: {e}")
        return default

def delete_file_safe(filepath: Union[str, Path], backup: bool = False) -> bool:
    """Safely delete a file with comprehensive error handling."""
    try:
        file_path = Path(filepath)
        
        if not file_path.exists():
            logger.warning(f"File does not exist: {file_path}")
            return True  # Consider it "deleted"
        
        if not file_path.is_file():
            logger.warning(f"Path is not a file: {file_path}")
            return False
        
        # Create backup if requested
        if backup:
            backup_path = file_path.with_suffix(f"{file_path.suffix}.deleted")
            try:
                shutil.copy2(file_path, backup_path)
                logger.debug(f"Created backup before deletion: {backup_path}")
            except Exception as e:
                logger.warning(f"Failed to create backup: {e}")
        
        # Delete the file
        file_path.unlink()
        
        logger.info(f"Deleted file: {file_path}")
        return True
        
    except PermissionError as e:
        logger.error(f"Permission denied deleting file {filepath}: {e}")
        raise StorageError(f"Permission denied deleting file {filepath}: {e}")
    except Exception as e:
        logger.error(f"Error deleting file {filepath}: {e}")
        return False

def delete_directory_safe(directory: Union[str, Path], 
                         recursive: bool = True, 
                         backup: bool = False) -> bool:
    """Safely delete a directory with comprehensive error handling."""
    try:
        dir_path = Path(directory)
        
        if not dir_path.exists():
            logger.warning(f"Directory does not exist: {dir_path}")
            return True  # Consider it "deleted"
        
        if not dir_path.is_dir():
            logger.warning(f"Path is not a directory: {dir_path}")
            return False
        
        # Create backup if requested
        if backup:
            backup_path = dir_path.with_suffix(f"{dir_path.suffix}.deleted")
            try:
                shutil.copytree(dir_path, backup_path)
                logger.debug(f"Created backup before deletion: {backup_path}")
            except Exception as e:
                logger.warning(f"Failed to create backup: {e}")
        
        # Delete the directory
        if recursive:
            shutil.rmtree(dir_path)
        else:
            dir_path.rmdir()
        
        logger.info(f"Deleted directory: {dir_path}")
        return True
        
    except PermissionError as e:
        logger.error(f"Permission denied deleting directory {directory}: {e}")
        raise StorageError(f"Permission denied deleting directory {directory}: {e}")
    except Exception as e:
        logger.error(f"Error deleting directory {directory}: {e}")
        return False

def copy_file_safe(src: Union[str, Path], dst: Union[str, Path], 
                   overwrite: bool = False) -> bool:
    """Safely copy a file with comprehensive error handling."""
    try:
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            logger.warning(f"Source file does not exist: {src_path}")
            return False
        
        if not src_path.is_file():
            logger.warning(f"Source path is not a file: {src_path}")
            return False
        
        if dst_path.exists() and not overwrite:
            logger.warning(f"Destination file exists and overwrite is False: {dst_path}")
            return False
        
        # Ensure destination directory exists
        ensure_file_directory(dst_path)
        
        # Copy the file
        shutil.copy2(src_path, dst_path)
        
        logger.info(f"Copied file: {src_path} -> {dst_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error copying file {src} to {dst}: {e}")
        return False

def move_file_safe(src: Union[str, Path], dst: Union[str, Path], 
                   overwrite: bool = False) -> bool:
    """Safely move a file with comprehensive error handling."""
    try:
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            logger.warning(f"Source file does not exist: {src_path}")
            return False
        
        if not src_path.is_file():
            logger.warning(f"Source path is not a file: {src_path}")
            return False
        
        if dst_path.exists() and not overwrite:
            logger.warning(f"Destination file exists and overwrite is False: {dst_path}")
            return False
        
        # Ensure destination directory exists
        ensure_file_directory(dst_path)
        
        # Move the file
        shutil.move(str(src_path), str(dst_path))
        
        logger.info(f"Moved file: {src_path} -> {dst_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error moving file {src} to {dst}: {e}")
        return False

def format_duration(seconds: Union[int, float]) -> str:
    """Format duration in seconds to readable string with comprehensive error handling."""
    try:
        if not isinstance(seconds, (int, float)):
            raise ValidationError(f"Invalid duration type: {type(seconds)}")
        
        if seconds < 0:
            raise ValidationError(f"Negative duration: {seconds}")
        
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
        
    except Exception as e:
        logger.error(f"Error formatting duration {seconds}: {e}")
        return "00:00"

def format_file_size(size_bytes: int) -> str:
    """Format file size in bytes to human readable string."""
    try:
        if size_bytes < 0:
            raise ValidationError(f"Negative file size: {size_bytes}")
        
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
        size_index = 0
        size = float(size_bytes)
        
        while size >= 1024 and size_index < len(size_names) - 1:
            size /= 1024
            size_index += 1
        
        return f"{size:.2f} {size_names[size_index]}"
        
    except Exception as e:
        logger.error(f"Error formatting file size {size_bytes}: {e}")
        return "Unknown"

def format_percentage(value: float, total: float) -> str:
    """Format percentage with comprehensive error handling."""
    try:
        if total == 0:
            return "0.00%"
        
        if value < 0 or total < 0:
            raise ValidationError(f"Negative values: {value}, {total}")
        
        percentage = (value / total) * 100
        return f"{percentage:.2f}%"
        
    except Exception as e:
        logger.error(f"Error formatting percentage {value}/{total}: {e}")
        return "0.00%"

def create_temp_file(suffix: str = "", prefix: str = "age_temp_") -> Path:
    """Create a temporary file with comprehensive error handling."""
    try:
        temp_file = tempfile.NamedTemporaryFile(
            suffix=suffix, 
            prefix=prefix, 
            delete=False
        )
        temp_path = Path(temp_file.name)
        temp_file.close()
        
        logger.debug(f"Created temporary file: {temp_path}")
        return temp_path
        
    except Exception as e:
        logger.error(f"Error creating temporary file: {e}")
        raise StorageError(f"Failed to create temporary file: {e}")

def create_temp_directory(prefix: str = "age_temp_") -> Path:
    """Create a temporary directory with comprehensive error handling."""
    try:
        temp_dir = tempfile.mkdtemp(prefix=prefix)
        temp_path = Path(temp_dir)
        
        logger.debug(f"Created temporary directory: {temp_path}")
        return temp_path
        
    except Exception as e:
        logger.error(f"Error creating temporary directory: {e}")
        raise StorageError(f"Failed to create temporary directory: {e}")

def cleanup_temp_files(temp_dir: Union[str, Path], 
                      max_age_hours: int = 24) -> int:
    """Clean up temporary files older than specified age."""
    try:
        temp_path = Path(temp_dir)
        
        if not temp_path.exists():
            logger.warning(f"Temp directory does not exist: {temp_path}")
            return 0
        
        if not temp_path.is_dir():
            logger.warning(f"Path is not a directory: {temp_path}")
            return 0
        
        cutoff_time = time.time() - (max_age_hours * 3600)
        cleaned_count = 0
        
        for file_path in temp_path.rglob('*'):
            try:
                if file_path.is_file():
                    file_age = file_path.stat().st_mtime
                    if file_age < cutoff_time:
                        file_path.unlink()
                        cleaned_count += 1
                        logger.debug(f"Cleaned up old temp file: {file_path}")
                        
            except (PermissionError, OSError) as e:
                logger.warning(f"Cannot clean up file {file_path}: {e}")
                continue
        
        logger.info(f"Cleaned up {cleaned_count} temporary files from {temp_path}")
        return cleaned_count
        
    except Exception as e:
        logger.error(f"Error cleaning up temp files {temp_dir}: {e}")
        return 0

def compress_file(filepath: Union[str, Path], 
                 compression_type: str = 'zip') -> Optional[Path]:
    """Compress a file with comprehensive error handling."""
    try:
        file_path = Path(filepath)
        
        if not file_path.exists():
            logger.warning(f"File does not exist: {file_path}")
            return None
        
        if not file_path.is_file():
            logger.warning(f"Path is not a file: {file_path}")
            return None
        
        # Determine output path
        if compression_type.lower() == 'zip':
            output_path = file_path.with_suffix(f"{file_path.suffix}.zip")
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(file_path, file_path.name)
        
        elif compression_type.lower() == 'gzip':
            output_path = file_path.with_suffix(f"{file_path.suffix}.gz")
            with open(file_path, 'rb') as f_in:
                with gzip.open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        
        elif compression_type.lower() == 'bz2':
            output_path = file_path.with_suffix(f"{file_path.suffix}.bz2")
            with open(file_path, 'rb') as f_in:
                with bz2.open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        
        else:
            raise ValidationError(f"Unsupported compression type: {compression_type}")
        
        logger.info(f"Compressed file: {file_path} -> {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error compressing file {filepath}: {e}")
        return None

def decompress_file(filepath: Union[str, Path], 
                   output_dir: Optional[Union[str, Path]] = None) -> Optional[Path]:
    """Decompress a file with comprehensive error handling."""
    try:
        file_path = Path(filepath)
        
        if not file_path.exists():
            logger.warning(f"File does not exist: {file_path}")
            return None
        
        if not file_path.is_file():
            logger.warning(f"Path is not a file: {file_path}")
            return None
        
        # Determine output directory
        if output_dir is None:
            output_dir = file_path.parent
        else:
            output_dir = Path(output_dir)
            ensure_directory(output_dir)
        
        # Determine compression type and decompress
        if file_path.suffix.lower() == '.zip':
            with zipfile.ZipFile(file_path, 'r') as zipf:
                zipf.extractall(output_dir)
            logger.info(f"Decompressed ZIP file: {file_path} -> {output_dir}")
            return output_dir
        
        elif file_path.suffix.lower() == '.gz':
            output_path = output_dir / file_path.stem
            with gzip.open(file_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            logger.info(f"Decompressed GZIP file: {file_path} -> {output_path}")
            return output_path
        
        elif file_path.suffix.lower() == '.bz2':
            output_path = output_dir / file_path.stem
            with bz2.open(file_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            logger.info(f"Decompressed BZ2 file: {file_path} -> {output_path}")
            return output_path
        
        else:
            logger.warning(f"Unknown compression type: {file_path.suffix}")
            return None
        
    except Exception as e:
        logger.error(f"Error decompressing file {filepath}: {e}")
        return None

def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information."""
    try:
        import platform
        import psutil
        
        # Basic system info
        system_info = {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'python_implementation': platform.python_implementation(),
        }
        
        # CPU info
        try:
            system_info.update({
                'cpu_count': psutil.cpu_count(),
                'cpu_count_logical': psutil.cpu_count(logical=True),
                'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                'cpu_percent': psutil.cpu_percent(interval=1),
            })
        except Exception as e:
            logger.warning(f"Error getting CPU info: {e}")
        
        # Memory info
        try:
            memory = psutil.virtual_memory()
            system_info.update({
                'memory_total_gb': round(memory.total / (1024**3), 2),
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'memory_used_gb': round(memory.used / (1024**3), 2),
                'memory_percent': memory.percent,
            })
        except Exception as e:
            logger.warning(f"Error getting memory info: {e}")
        
        # Disk info
        try:
            disk = psutil.disk_usage('.')
            system_info.update({
                'disk_total_gb': round(disk.total / (1024**3), 2),
                'disk_used_gb': round(disk.used / (1024**3), 2),
                'disk_free_gb': round(disk.free / (1024**3), 2),
                'disk_percent': round((disk.used / disk.total) * 100, 2),
            })
        except Exception as e:
            logger.warning(f"Error getting disk info: {e}")
        
        # Network info
        try:
            network = psutil.net_io_counters()
            system_info.update({
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv,
                'network_packets_sent': network.packets_sent,
                'network_packets_recv': network.packets_recv,
            })
        except Exception as e:
            logger.warning(f"Error getting network info: {e}")
        
        logger.debug("Retrieved system information")
        return system_info
        
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return {
            'platform': 'Unknown',
            'platform_version': 'Unknown',
            'architecture': 'Unknown',
            'processor': 'Unknown',
            'python_version': 'Unknown',
            'python_implementation': 'Unknown',
            'error': str(e)
        }

def check_disk_space(path: Union[str, Path], required_gb: float = 1.0) -> bool:
    """Check if there's enough disk space."""
    try:
        path_obj = Path(path)
        
        # Get disk usage for the path
        disk_usage = psutil.disk_usage(str(path_obj))
        free_gb = disk_usage.free / (1024**3)
        
        has_space = free_gb >= required_gb
        
        if not has_space:
            logger.warning(f"Insufficient disk space: {free_gb:.2f}GB available, {required_gb}GB required")
        else:
            logger.debug(f"Disk space check passed: {free_gb:.2f}GB available")
        
        return has_space
        
    except Exception as e:
        logger.error(f"Error checking disk space {path}: {e}")
        return False

def check_memory_usage(required_mb: float = 100.0) -> bool:
    """Check if there's enough memory available."""
    try:
        memory = psutil.virtual_memory()
        available_mb = memory.available / (1024**2)
        
        has_memory = available_mb >= required_mb
        
        if not has_memory:
            logger.warning(f"Insufficient memory: {available_mb:.2f}MB available, {required_mb}MB required")
        else:
            logger.debug(f"Memory check passed: {available_mb:.2f}MB available")
        
        return has_memory
        
    except Exception as e:
        logger.error(f"Error checking memory usage: {e}")
        return False

def retry_operation(func: Callable, max_retries: int = 3, 
                   delay: float = 1.0, backoff: float = 2.0) -> Any:
    """Retry an operation with exponential backoff."""
    try:
        for attempt in range(max_retries + 1):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"Operation failed after {max_retries} retries: {e}")
                    raise e
                
                wait_time = delay * (backoff ** attempt)
                logger.warning(f"Operation failed (attempt {attempt + 1}/{max_retries + 1}), retrying in {wait_time:.2f}s: {e}")
                time.sleep(wait_time)
        
    except Exception as e:
        logger.error(f"Error in retry operation: {e}")
        raise e

def run_command(command: Union[str, List[str]], 
               timeout: int = 30, 
               cwd: Optional[Union[str, Path]] = None) -> Tuple[int, str, str]:
    """Run a system command with comprehensive error handling."""
    try:
        if isinstance(command, str):
            command = command.split()
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd
        )
        
        logger.debug(f"Command executed: {' '.join(command)}")
        logger.debug(f"Return code: {result.returncode}")
        
        if result.stdout:
            logger.debug(f"STDOUT: {result.stdout}")
        if result.stderr:
            logger.debug(f"STDERR: {result.stderr}")
        
        return result.returncode, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timed out: {' '.join(command)}")
        return -1, "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        logger.error(f"Error running command {' '.join(command)}: {e}")
        return -1, "", str(e)

def clear_cache() -> None:
    """Clear the file cache."""
    try:
        file_cache.clear()
        logger.info("File cache cleared")
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    try:
        return {
            'size': file_cache.size(),
            'max_size': file_cache.max_size,
            'ttl': file_cache.ttl
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {'size': 0, 'max_size': 0, 'ttl': 0}

# Legacy functions for backward compatibility
def get_timestamp():
    """Legacy function for backward compatibility."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def ensure_directory(path):
    """Legacy function for backward compatibility."""
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            path_obj.mkdir(parents=True, exist_ok=True)
        return path_obj
    except Exception as e:
        logger.error(f"Error ensuring directory {path}: {e}")
        raise StorageError(f"Failed to ensure directory {path}: {e}")

def get_file_size_mb(filepath):
    """Legacy function for backward compatibility."""
    try:
        file_path = Path(filepath)
        if not file_path.exists() or not file_path.is_file():
            return 0.0
        size_bytes = file_path.stat().st_size
        return size_bytes / (1024 * 1024)
    except Exception as e:
        logger.error(f"Error getting file size {filepath}: {e}")
        return 0.0

def get_directory_size_gb(directory):
    """Legacy function for backward compatibility."""
    try:
        dir_path = Path(directory)
        if not dir_path.exists() or not dir_path.is_dir():
            return 0.0
        total_size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
        return total_size / (1024 * 1024 * 1024)
    except Exception as e:
        logger.error(f"Error getting directory size {directory}: {e}")
        return 0.0

def save_json(data, filepath):
    """Legacy function for backward compatibility."""
    try:
        file_path = Path(filepath)
        ensure_file_directory(file_path)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON {filepath}: {e}")
        return False

def load_json(filepath):
    """Legacy function for backward compatibility."""
    try:
        file_path = Path(filepath)
        if not file_path.exists():
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON {filepath}: {e}")
        return None

def delete_file_safe(filepath):
    """Legacy function for backward compatibility."""
    try:
        file_path = Path(filepath)
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting file {filepath}: {e}")
        return False

def delete_directory_safe(directory):
    """Legacy function for backward compatibility."""
    try:
        dir_path = Path(directory)
        if dir_path.exists() and dir_path.is_dir():
            shutil.rmtree(dir_path)
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting directory {directory}: {e}")
        return False

def format_duration(seconds):
    """Legacy function for backward compatibility."""
    try:
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    except Exception as e:
        logger.error(f"Error formatting duration {seconds}: {e}")
        return f"{seconds}s"
