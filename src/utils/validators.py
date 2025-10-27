"""Enhanced input validation utilities with comprehensive error handling and edge case management."""

import os
import re
import json
import yaml
import hashlib
import mimetypes
import tempfile
import shutil
import psutil
import platform
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple, Callable
from datetime import datetime, timedelta
import logging

from .constants import (
    validate_fps, validate_sample_rate, validate_window_size,
    validate_temperature, validate_memory_limit, validate_file_format,
    validate_theme, validate_provider, validate_model, validate_storage_path,
    validate_filename, validate_duration, validate_quality, validate_chunk_size,
    validate_channels, validate_max_tokens, validate_timeout, validate_max_retries,
    validate_retry_delay, validate_requests_per_minute, validate_requests_per_hour,
    validate_cpu_limit, validate_max_workers, validate_processing_timeout,
    validate_cache_size, validate_storage_size, validate_cleanup_interval,
    validate_backup_retention, validate_font_size, validate_font_family,
    validate_animation_duration, validate_blur_radius, validate_blur_level,
    validate_encryption_algorithm, validate_key_length, validate_permission
)
from ..error_handling.exceptions import (
    ValidationError, StorageError, ConfigurationError,
    handle_exception
)

# Initialize logger
logger = logging.getLogger(__name__)

class ValidationResult:
    """Enhanced validation result with detailed information."""
    
    def __init__(self, is_valid: bool, message: str = "", 
                 details: Optional[Dict[str, Any]] = None,
                 suggestions: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.message = message
        self.details = details or {}
        self.suggestions = suggestions or []
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'is_valid': self.is_valid,
            'message': self.message,
            'details': self.details,
            'suggestions': self.suggestions,
            'timestamp': self.timestamp.isoformat()
        }
    
    def __bool__(self) -> bool:
        return self.is_valid

def validate_api_key(api_key: str, provider: str = "generic") -> ValidationResult:
    """Validate API key format with comprehensive error handling."""
    try:
        if not api_key:
            return ValidationResult(
                False, 
                "API key is required",
                suggestions=["Provide a valid API key"]
            )
        
        if not isinstance(api_key, str):
            return ValidationResult(
                False,
                "API key must be a string",
                suggestions=["Convert API key to string format"]
            )
        
        # Provider-specific validation
        if provider.lower() == "gemini":
            if len(api_key) < 20:
                return ValidationResult(
                    False,
                    "Gemini API key appears too short",
                    suggestions=["Check if the API key is complete"]
                )
            if not api_key.startswith(('AIza', 'AI')):
                return ValidationResult(
                    False,
                    "Gemini API key format appears invalid",
                    suggestions=["Verify the API key format for Gemini"]
                )
        
        elif provider.lower() == "openai":
            if len(api_key) < 20:
                return ValidationResult(
                    False,
                    "OpenAI API key appears too short",
                    suggestions=["Check if the API key is complete"]
                )
            if not api_key.startswith('sk-'):
                return ValidationResult(
                    False,
                    "OpenAI API key format appears invalid",
                    suggestions=["Verify the API key format for OpenAI"]
                )
        
        else:
            # Generic validation
            if len(api_key) < 10:
                return ValidationResult(
                    False,
                    "API key appears too short",
                    suggestions=["Check if the API key is complete"]
                )
        
        # Check for common invalid characters
        invalid_chars = [' ', '\n', '\t', '\r']
        if any(char in api_key for char in invalid_chars):
            return ValidationResult(
                False,
                "API key contains invalid characters",
                suggestions=["Remove spaces, newlines, or tabs from the API key"]
            )
        
        logger.debug(f"API key validation passed for provider: {provider}")
        return ValidationResult(True, "API key format is valid")
        
    except Exception as e:
        logger.error(f"Error validating API key: {e}")
        return ValidationResult(
            False,
            f"API key validation failed: {e}",
            suggestions=["Check API key format and try again"]
        )

def validate_directory_writable(path: Union[str, Path]) -> ValidationResult:
    """Check if directory is writable with comprehensive error handling."""
    try:
        path_obj = Path(path)
        
        # Check if path is valid
        if not validate_storage_path(str(path_obj)):
            return ValidationResult(
                False,
                f"Invalid directory path: {path}",
                suggestions=["Use a valid directory path"]
            )
        
        # Create directory if it doesn't exist
        try:
            path_obj.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            return ValidationResult(
                False,
                f"Permission denied creating directory: {path}",
                suggestions=["Run with appropriate permissions", "Check directory permissions"]
            )
        except Exception as e:
            return ValidationResult(
                False,
                f"Failed to create directory: {e}",
                suggestions=["Check path validity and permissions"]
            )
        
        # Test write permissions
        test_file = path_obj / '.write_test'
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            
            # Test read permissions
            with open(test_file, 'r') as f:
                content = f.read()
                if content != 'test':
                    return ValidationResult(
                        False,
                        "Directory write test failed - content mismatch",
                        suggestions=["Check directory permissions"]
                    )
            
            # Clean up test file
            test_file.unlink()
            
            logger.debug(f"Directory writable validation passed: {path}")
            return ValidationResult(True, f"Directory is writable: {path}")
            
        except PermissionError:
            return ValidationResult(
                False,
                f"Permission denied writing to directory: {path}",
                suggestions=["Run with appropriate permissions", "Check directory permissions"]
            )
        except Exception as e:
            return ValidationResult(
                False,
                f"Directory write test failed: {e}",
                suggestions=["Check directory permissions and disk space"]
            )
        
    except Exception as e:
        logger.error(f"Error validating directory writable {path}: {e}")
        return ValidationResult(
            False,
            f"Directory validation failed: {e}",
            suggestions=["Check path validity and permissions"]
        )

def validate_disk_space(path: Union[str, Path], required_gb: float = 1.0) -> ValidationResult:
    """Check if sufficient disk space is available with comprehensive error handling."""
    try:
        path_obj = Path(path)
        
        # Ensure path exists
        if not path_obj.exists():
            path_obj.mkdir(parents=True, exist_ok=True)
        
        # Get disk usage
        try:
            disk_usage = psutil.disk_usage(str(path_obj))
            free_gb = disk_usage.free / (1024**3)
            total_gb = disk_usage.total / (1024**3)
            used_gb = disk_usage.used / (1024**3)
            
            has_space = free_gb >= required_gb
            
            if has_space:
                logger.debug(f"Disk space check passed: {free_gb:.2f}GB available")
                return ValidationResult(
                    True,
                    f"Sufficient disk space available: {free_gb:.2f}GB",
                    details={
                        'free_gb': free_gb,
                        'total_gb': total_gb,
                        'used_gb': used_gb,
                        'required_gb': required_gb
                    }
                )
            else:
                logger.warning(f"Insufficient disk space: {free_gb:.2f}GB available, {required_gb}GB required")
                return ValidationResult(
                    False,
                    f"Insufficient disk space: {free_gb:.2f}GB available, {required_gb}GB required",
                    details={
                        'free_gb': free_gb,
                        'total_gb': total_gb,
                        'used_gb': used_gb,
                        'required_gb': required_gb
                    },
                    suggestions=[
                        "Free up disk space",
                        "Use a different storage location",
                        "Reduce required space requirements"
                    ]
                )
                
        except Exception as e:
            logger.error(f"Error checking disk space: {e}")
            return ValidationResult(
                False,
                f"Failed to check disk space: {e}",
                suggestions=["Check disk permissions and availability"]
            )
        
    except Exception as e:
        logger.error(f"Error validating disk space {path}: {e}")
        return ValidationResult(
            False,
            f"Disk space validation failed: {e}",
            suggestions=["Check path validity and disk availability"]
        )

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to remove invalid characters with comprehensive error handling."""
    try:
        if not filename:
            return "unnamed_file"
        
        if not isinstance(filename, str):
            filename = str(filename)
        
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove control characters
        filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
        
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        
        # Limit length
        if len(filename) > 200:
            filename = filename[:200]
        
        # Ensure filename is not empty
        if not filename:
            filename = "unnamed_file"
        
        logger.debug(f"Sanitized filename: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Error sanitizing filename {filename}: {e}")
        return "unnamed_file"

def validate_file_path(filepath: Union[str, Path], 
                      must_exist: bool = False,
                      must_be_file: bool = True,
                      must_be_directory: bool = False) -> ValidationResult:
    """Validate file path with comprehensive error handling."""
    try:
        path_obj = Path(filepath)
        
        # Check if path is valid
        if not validate_storage_path(str(path_obj)):
            return ValidationResult(
                False,
                f"Invalid file path: {filepath}",
                suggestions=["Use a valid file path"]
            )
        
        # Check if path exists
        if must_exist and not path_obj.exists():
            return ValidationResult(
                False,
                f"File path does not exist: {filepath}",
                suggestions=["Create the file or use an existing path"]
            )
        
        # Check if it's a file
        if must_be_file and path_obj.exists() and not path_obj.is_file():
            return ValidationResult(
                False,
                f"Path is not a file: {filepath}",
                suggestions=["Use a file path instead of directory"]
            )
        
        # Check if it's a directory
        if must_be_directory and path_obj.exists() and not path_obj.is_dir():
            return ValidationResult(
                False,
                f"Path is not a directory: {filepath}",
                suggestions=["Use a directory path instead of file"]
            )
        
        logger.debug(f"File path validation passed: {filepath}")
        return ValidationResult(True, f"File path is valid: {filepath}")
        
    except Exception as e:
        logger.error(f"Error validating file path {filepath}: {e}")
        return ValidationResult(
            False,
            f"File path validation failed: {e}",
            suggestions=["Check path validity and format"]
        )

def validate_json_data(data: Any) -> ValidationResult:
    """Validate JSON data with comprehensive error handling."""
    try:
        if data is None:
            return ValidationResult(
                False,
                "JSON data is None",
                suggestions=["Provide valid JSON data"]
            )
        
        # Try to serialize the data
        try:
            json.dumps(data)
        except TypeError as e:
            return ValidationResult(
                False,
                f"JSON serialization failed: {e}",
                suggestions=["Ensure all data is JSON serializable"]
            )
        
        # Check for common issues
        if isinstance(data, dict):
            # Check for circular references
            try:
                json.dumps(data, default=str)
            except (TypeError, ValueError) as e:
                return ValidationResult(
                    False,
                    f"JSON contains circular references or invalid data: {e}",
                    suggestions=["Remove circular references", "Use default serialization"]
                )
        
        logger.debug("JSON data validation passed")
        return ValidationResult(True, "JSON data is valid")
        
    except Exception as e:
        logger.error(f"Error validating JSON data: {e}")
        return ValidationResult(
            False,
            f"JSON validation failed: {e}",
            suggestions=["Check data format and content"]
        )

def validate_yaml_data(data: Any) -> ValidationResult:
    """Validate YAML data with comprehensive error handling."""
    try:
        if data is None:
            return ValidationResult(
                False,
                "YAML data is None",
                suggestions=["Provide valid YAML data"]
            )
        
        # Try to serialize the data
        try:
            yaml.dump(data)
        except Exception as e:
            return ValidationResult(
                False,
                f"YAML serialization failed: {e}",
                suggestions=["Ensure all data is YAML serializable"]
            )
        
        logger.debug("YAML data validation passed")
        return ValidationResult(True, "YAML data is valid")
        
    except Exception as e:
        logger.error(f"Error validating YAML data: {e}")
        return ValidationResult(
            False,
            f"YAML validation failed: {e}",
            suggestions=["Check data format and content"]
        )

def validate_configuration(config: Dict[str, Any]) -> ValidationResult:
    """Validate configuration with comprehensive error handling."""
    try:
        if not isinstance(config, dict):
            return ValidationResult(
                False,
                "Configuration must be a dictionary",
                suggestions=["Provide configuration as a dictionary"]
            )
        
        # Check required sections
        required_sections = ['recording', 'storage', 'llm']
        missing_sections = [section for section in required_sections if section not in config]
        
        if missing_sections:
            return ValidationResult(
                False,
                f"Missing required configuration sections: {missing_sections}",
                suggestions=["Add missing configuration sections"]
            )
        
        # Validate recording section
        if 'recording' in config:
            recording_result = validate_recording_config(config['recording'])
            if not recording_result.is_valid:
                return recording_result
        
        # Validate storage section
        if 'storage' in config:
            storage_result = validate_storage_config(config['storage'])
            if not storage_result.is_valid:
                return storage_result
        
        # Validate LLM section
        if 'llm' in config:
            llm_result = validate_llm_config(config['llm'])
            if not llm_result.is_valid:
                return llm_result
        
        logger.debug("Configuration validation passed")
        return ValidationResult(True, "Configuration is valid")
        
    except Exception as e:
        logger.error(f"Error validating configuration: {e}")
        return ValidationResult(
            False,
            f"Configuration validation failed: {e}",
            suggestions=["Check configuration format and content"]
        )

def validate_recording_config(config: Dict[str, Any]) -> ValidationResult:
    """Validate recording configuration."""
    try:
        if not isinstance(config, dict):
            return ValidationResult(
                False,
                "Recording configuration must be a dictionary",
                suggestions=["Provide recording configuration as a dictionary"]
            )
        
        # Validate FPS
        if 'fps' in config:
            if not validate_fps(config['fps']):
                return ValidationResult(
                    False,
                    f"Invalid FPS value: {config['fps']}",
                    suggestions=["Use FPS between 1 and 30"]
                )
        
        # Validate sample rate
        if 'audio_sample_rate' in config:
            if not validate_sample_rate(config['audio_sample_rate']):
                return ValidationResult(
                    False,
                    f"Invalid audio sample rate: {config['audio_sample_rate']}",
                    suggestions=["Use sample rate between 8000 and 48000 Hz"]
                )
        
        # Validate duration
        if 'max_duration_minutes' in config:
            duration_seconds = config['max_duration_minutes'] * 60
            if not validate_duration(duration_seconds):
                return ValidationResult(
                    False,
                    f"Invalid max duration: {config['max_duration_minutes']} minutes",
                    suggestions=["Use duration between 1 and 3600 seconds"]
                )
        
        logger.debug("Recording configuration validation passed")
        return ValidationResult(True, "Recording configuration is valid")
        
    except Exception as e:
        logger.error(f"Error validating recording configuration: {e}")
        return ValidationResult(
            False,
            f"Recording configuration validation failed: {e}",
            suggestions=["Check recording configuration format and values"]
        )

def validate_storage_config(config: Dict[str, Any]) -> ValidationResult:
    """Validate storage configuration."""
    try:
        if not isinstance(config, dict):
            return ValidationResult(
                False,
                "Storage configuration must be a dictionary",
                suggestions=["Provide storage configuration as a dictionary"]
            )
        
        # Validate paths
        path_fields = ['local_path', 'temp_path', 'recordings_path', 'processed_path']
        for field in path_fields:
            if field in config:
                path_result = validate_file_path(config[field], must_be_directory=True)
                if not path_result.is_valid:
                    return path_result
        
        # Validate storage size
        if 'max_storage_gb' in config:
            if not validate_storage_size(config['max_storage_gb']):
                return ValidationResult(
                    False,
                    f"Invalid max storage size: {config['max_storage_gb']} GB",
                    suggestions=["Use storage size between 0.1 and 100 GB"]
                )
        
        logger.debug("Storage configuration validation passed")
        return ValidationResult(True, "Storage configuration is valid")
        
    except Exception as e:
        logger.error(f"Error validating storage configuration: {e}")
        return ValidationResult(
            False,
            f"Storage configuration validation failed: {e}",
            suggestions=["Check storage configuration format and values"]
        )

def validate_llm_config(config: Dict[str, Any]) -> ValidationResult:
    """Validate LLM configuration."""
    try:
        if not isinstance(config, dict):
            return ValidationResult(
                False,
                "LLM configuration must be a dictionary",
                suggestions=["Provide LLM configuration as a dictionary"]
            )
        
        # Validate provider
        if 'provider' in config:
            if not validate_provider(config['provider']):
                return ValidationResult(
                    False,
                    f"Invalid LLM provider: {config['provider']}",
                    suggestions=["Use supported providers: gemini, openai, local"]
                )
        
        # Validate model
        if 'model' in config and 'provider' in config:
            if not validate_model(config['model'], config['provider']):
                return ValidationResult(
                    False,
                    f"Invalid model for provider {config['provider']}: {config['model']}",
                    suggestions=["Use a valid model for the selected provider"]
                )
        
        # Validate temperature
        if 'temperature' in config:
            if not validate_temperature(config['temperature']):
                return ValidationResult(
                    False,
                    f"Invalid temperature: {config['temperature']}",
                    suggestions=["Use temperature between 0.0 and 2.0"]
                )
        
        # Validate max tokens
        if 'max_tokens' in config:
            if not validate_max_tokens(config['max_tokens']):
                return ValidationResult(
                    False,
                    f"Invalid max tokens: {config['max_tokens']}",
                    suggestions=["Use max tokens between 100 and 8000"]
                )
        
        logger.debug("LLM configuration validation passed")
        return ValidationResult(True, "LLM configuration is valid")
        
    except Exception as e:
        logger.error(f"Error validating LLM configuration: {e}")
        return ValidationResult(
            False,
            f"LLM configuration validation failed: {e}",
            suggestions=["Check LLM configuration format and values"]
        )

def validate_session_data(session_data: Dict[str, Any]) -> ValidationResult:
    """Validate session data with comprehensive error handling."""
    try:
        if not isinstance(session_data, dict):
            return ValidationResult(
                False,
                "Session data must be a dictionary",
                suggestions=["Provide session data as a dictionary"]
            )
        
        # Check required fields
        required_fields = ['session_id', 'start_time', 'end_time']
        missing_fields = [field for field in required_fields if field not in session_data]
        
        if missing_fields:
            return ValidationResult(
                False,
                f"Missing required session fields: {missing_fields}",
                suggestions=["Add missing session data fields"]
            )
        
        # Validate session ID
        if not session_data['session_id']:
            return ValidationResult(
                False,
                "Session ID cannot be empty",
                suggestions=["Provide a valid session ID"]
            )
        
        # Validate timestamps
        try:
            start_time = datetime.fromisoformat(session_data['start_time'])
            end_time = datetime.fromisoformat(session_data['end_time'])
            
            if start_time >= end_time:
                return ValidationResult(
                    False,
                    "Start time must be before end time",
                    suggestions=["Check session timestamps"]
                )
            
            # Check session duration
            duration = (end_time - start_time).total_seconds()
            if not validate_duration(duration):
                return ValidationResult(
                    False,
                    f"Invalid session duration: {duration} seconds",
                    suggestions=["Use session duration between 1 and 3600 seconds"]
                )
                
        except ValueError as e:
            return ValidationResult(
                False,
                f"Invalid timestamp format: {e}",
                suggestions=["Use ISO format for timestamps"]
            )
        
        logger.debug("Session data validation passed")
        return ValidationResult(True, "Session data is valid")
        
    except Exception as e:
        logger.error(f"Error validating session data: {e}")
        return ValidationResult(
            False,
            f"Session data validation failed: {e}",
            suggestions=["Check session data format and content"]
        )

def validate_workflow_data(workflow_data: List[Dict[str, Any]]) -> ValidationResult:
    """Validate workflow data with comprehensive error handling."""
    try:
        if not isinstance(workflow_data, list):
            return ValidationResult(
                False,
                "Workflow data must be a list",
                suggestions=["Provide workflow data as a list"]
            )
        
        if not workflow_data:
            return ValidationResult(
                False,
                "Workflow data cannot be empty",
                suggestions=["Provide at least one workflow"]
            )
        
        # Validate each workflow
        for i, workflow in enumerate(workflow_data):
            if not isinstance(workflow, dict):
                return ValidationResult(
                    False,
                    f"Workflow {i} must be a dictionary",
                    suggestions=["Provide workflow as a dictionary"]
                )
            
            # Check required fields
            required_fields = ['description', 'steps']
            missing_fields = [field for field in required_fields if field not in workflow]
            
            if missing_fields:
                return ValidationResult(
                    False,
                    f"Missing required workflow fields in workflow {i}: {missing_fields}",
                    suggestions=["Add missing workflow fields"]
                )
            
            # Validate description
            if not workflow['description']:
                return ValidationResult(
                    False,
                    f"Workflow {i} description cannot be empty",
                    suggestions=["Provide a valid workflow description"]
                )
            
            # Validate steps
            if not isinstance(workflow['steps'], list):
                return ValidationResult(
                    False,
                    f"Workflow {i} steps must be a list",
                    suggestions=["Provide workflow steps as a list"]
                )
            
            if not workflow['steps']:
                return ValidationResult(
                    False,
                    f"Workflow {i} steps cannot be empty",
                    suggestions=["Provide at least one workflow step"]
                )
        
        logger.debug("Workflow data validation passed")
        return ValidationResult(True, "Workflow data is valid")
        
    except Exception as e:
        logger.error(f"Error validating workflow data: {e}")
        return ValidationResult(
            False,
            f"Workflow data validation failed: {e}",
            suggestions=["Check workflow data format and content"]
        )

def validate_audio_file(filepath: Union[str, Path]) -> ValidationResult:
    """Validate audio file with comprehensive error handling."""
    try:
        path_obj = Path(filepath)
        
        # Check if file exists
        if not path_obj.exists():
            return ValidationResult(
                False,
                f"Audio file does not exist: {filepath}",
                suggestions=["Create the audio file or use an existing path"]
            )
        
        # Check if it's a file
        if not path_obj.is_file():
            return ValidationResult(
                False,
                f"Path is not a file: {filepath}",
                suggestions=["Use a file path instead of directory"]
            )
        
        # Check file size
        file_size = path_obj.stat().st_size
        if file_size == 0:
            return ValidationResult(
                False,
                "Audio file is empty",
                suggestions=["Provide a non-empty audio file"]
            )
        
        # Check file extension
        audio_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac']
        if path_obj.suffix.lower() not in audio_extensions:
            return ValidationResult(
                False,
                f"Unsupported audio format: {path_obj.suffix}",
                suggestions=[f"Use supported audio formats: {', '.join(audio_extensions)}"]
            )
        
        # Check MIME type
        mime_type = mimetypes.guess_type(str(path_obj))[0]
        if mime_type and not mime_type.startswith('audio/'):
            return ValidationResult(
                False,
                f"File does not appear to be audio: {mime_type}",
                suggestions=["Use a valid audio file"]
            )
        
        logger.debug(f"Audio file validation passed: {filepath}")
        return ValidationResult(True, f"Audio file is valid: {filepath}")
        
    except Exception as e:
        logger.error(f"Error validating audio file {filepath}: {e}")
        return ValidationResult(
            False,
            f"Audio file validation failed: {e}",
            suggestions=["Check file path and format"]
        )

def validate_video_file(filepath: Union[str, Path]) -> ValidationResult:
    """Validate video file with comprehensive error handling."""
    try:
        path_obj = Path(filepath)
        
        # Check if file exists
        if not path_obj.exists():
            return ValidationResult(
                False,
                f"Video file does not exist: {filepath}",
                suggestions=["Create the video file or use an existing path"]
            )
        
        # Check if it's a file
        if not path_obj.is_file():
            return ValidationResult(
                False,
                f"Path is not a file: {filepath}",
                suggestions=["Use a file path instead of directory"]
            )
        
        # Check file size
        file_size = path_obj.stat().st_size
        if file_size == 0:
            return ValidationResult(
                False,
                "Video file is empty",
                suggestions=["Provide a non-empty video file"]
            )
        
        # Check file extension
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
        if path_obj.suffix.lower() not in video_extensions:
            return ValidationResult(
                False,
                f"Unsupported video format: {path_obj.suffix}",
                suggestions=[f"Use supported video formats: {', '.join(video_extensions)}"]
            )
        
        # Check MIME type
        mime_type = mimetypes.guess_type(str(path_obj))[0]
        if mime_type and not mime_type.startswith('video/'):
            return ValidationResult(
                False,
                f"File does not appear to be video: {mime_type}",
                suggestions=["Use a valid video file"]
            )
        
        logger.debug(f"Video file validation passed: {filepath}")
        return ValidationResult(True, f"Video file is valid: {filepath}")
        
    except Exception as e:
        logger.error(f"Error validating video file {filepath}: {e}")
        return ValidationResult(
            False,
            f"Video file validation failed: {e}",
            suggestions=["Check file path and format"]
        )

def validate_image_file(filepath: Union[str, Path]) -> ValidationResult:
    """Validate image file with comprehensive error handling."""
    try:
        path_obj = Path(filepath)
        
        # Check if file exists
        if not path_obj.exists():
            return ValidationResult(
                False,
                f"Image file does not exist: {filepath}",
                suggestions=["Create the image file or use an existing path"]
            )
        
        # Check if it's a file
        if not path_obj.is_file():
            return ValidationResult(
                False,
                f"Path is not a file: {filepath}",
                suggestions=["Use a file path instead of directory"]
            )
        
        # Check file size
        file_size = path_obj.stat().st_size
        if file_size == 0:
            return ValidationResult(
                False,
                "Image file is empty",
                suggestions=["Provide a non-empty image file"]
            )
        
        # Check file extension
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']
        if path_obj.suffix.lower() not in image_extensions:
            return ValidationResult(
                False,
                f"Unsupported image format: {path_obj.suffix}",
                suggestions=[f"Use supported image formats: {', '.join(image_extensions)}"]
            )
        
        # Check MIME type
        mime_type = mimetypes.guess_type(str(path_obj))[0]
        if mime_type and not mime_type.startswith('image/'):
            return ValidationResult(
                False,
                f"File does not appear to be image: {mime_type}",
                suggestions=["Use a valid image file"]
            )
        
        logger.debug(f"Image file validation passed: {filepath}")
        return ValidationResult(True, f"Image file is valid: {filepath}")
        
    except Exception as e:
        logger.error(f"Error validating image file {filepath}: {e}")
        return ValidationResult(
            False,
            f"Image file validation failed: {e}",
            suggestions=["Check file path and format"]
        )

def validate_url(url: str) -> ValidationResult:
    """Validate URL with comprehensive error handling."""
    try:
        if not url:
            return ValidationResult(
                False,
                "URL cannot be empty",
                suggestions=["Provide a valid URL"]
            )
        
        if not isinstance(url, str):
            return ValidationResult(
                False,
                "URL must be a string",
                suggestions=["Convert URL to string format"]
            )
        
        # Basic URL pattern validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            return ValidationResult(
                False,
                f"Invalid URL format: {url}",
                suggestions=["Use a valid URL format (e.g., https://example.com)"]
            )
        
        logger.debug(f"URL validation passed: {url}")
        return ValidationResult(True, f"URL is valid: {url}")
        
    except Exception as e:
        logger.error(f"Error validating URL {url}: {e}")
        return ValidationResult(
            False,
            f"URL validation failed: {e}",
            suggestions=["Check URL format and content"]
        )

def validate_email(email: str) -> ValidationResult:
    """Validate email address with comprehensive error handling."""
    try:
        if not email:
            return ValidationResult(
                False,
                "Email cannot be empty",
                suggestions=["Provide a valid email address"]
            )
        
        if not isinstance(email, str):
            return ValidationResult(
                False,
                "Email must be a string",
                suggestions=["Convert email to string format"]
            )
        
        # Email pattern validation
        email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        if not email_pattern.match(email):
            return ValidationResult(
                False,
                f"Invalid email format: {email}",
                suggestions=["Use a valid email format (e.g., user@example.com)"]
            )
        
        logger.debug(f"Email validation passed: {email}")
        return ValidationResult(True, f"Email is valid: {email}")
        
    except Exception as e:
        logger.error(f"Error validating email {email}: {e}")
        return ValidationResult(
            False,
            f"Email validation failed: {e}",
            suggestions=["Check email format and content"]
        )

def validate_phone_number(phone: str) -> ValidationResult:
    """Validate phone number with comprehensive error handling."""
    try:
        if not phone:
            return ValidationResult(
                False,
                "Phone number cannot be empty",
                suggestions=["Provide a valid phone number"]
            )
        
        if not isinstance(phone, str):
            return ValidationResult(
                False,
                "Phone number must be a string",
                suggestions=["Convert phone number to string format"]
            )
        
        # Remove common formatting characters
        cleaned_phone = re.sub(r'[^\d+]', '', phone)
        
        # Basic phone number validation
        if len(cleaned_phone) < 10:
            return ValidationResult(
                False,
                f"Phone number too short: {phone}",
                suggestions=["Use a phone number with at least 10 digits"]
            )
        
        if len(cleaned_phone) > 15:
            return ValidationResult(
                False,
                f"Phone number too long: {phone}",
                suggestions=["Use a phone number with at most 15 digits"]
            )
        
        logger.debug(f"Phone number validation passed: {phone}")
        return ValidationResult(True, f"Phone number is valid: {phone}")
        
    except Exception as e:
        logger.error(f"Error validating phone number {phone}: {e}")
        return ValidationResult(
            False,
            f"Phone number validation failed: {e}",
            suggestions=["Check phone number format and content"]
        )

def validate_hash(hash_value: str, algorithm: str = 'sha256') -> ValidationResult:
    """Validate hash value with comprehensive error handling."""
    try:
        if not hash_value:
            return ValidationResult(
                False,
                "Hash value cannot be empty",
                suggestions=["Provide a valid hash value"]
            )
        
        if not isinstance(hash_value, str):
            return ValidationResult(
                False,
                "Hash value must be a string",
                suggestions=["Convert hash value to string format"]
            )
        
        # Check if hash contains only valid characters
        if not re.match(r'^[a-fA-F0-9]+$', hash_value):
            return ValidationResult(
                False,
                f"Invalid hash format: {hash_value}",
                suggestions=["Use hexadecimal characters only"]
            )
        
        # Check hash length based on algorithm
        expected_lengths = {
            'md5': 32,
            'sha1': 40,
            'sha256': 64,
            'sha512': 128
        }
        
        if algorithm in expected_lengths:
            expected_length = expected_lengths[algorithm]
            if len(hash_value) != expected_length:
                return ValidationResult(
                    False,
                    f"Invalid hash length for {algorithm}: {len(hash_value)} (expected {expected_length})",
                    suggestions=[f"Use {algorithm} hash with {expected_length} characters"]
                )
        
        logger.debug(f"Hash validation passed: {hash_value}")
        return ValidationResult(True, f"Hash is valid: {hash_value}")
        
    except Exception as e:
        logger.error(f"Error validating hash {hash_value}: {e}")
        return ValidationResult(
            False,
            f"Hash validation failed: {e}",
            suggestions=["Check hash format and content"]
        )

def validate_permissions(permissions: List[str]) -> ValidationResult:
    """Validate permissions list with comprehensive error handling."""
    try:
        if not isinstance(permissions, list):
            return ValidationResult(
                False,
                "Permissions must be a list",
                suggestions=["Provide permissions as a list"]
            )
        
        if not permissions:
            return ValidationResult(
                False,
                "Permissions list cannot be empty",
                suggestions=["Provide at least one permission"]
            )
        
        # Check each permission
        for permission in permissions:
            if not isinstance(permission, str):
                return ValidationResult(
                    False,
                    f"Permission must be a string: {permission}",
                    suggestions=["Convert permission to string format"]
                )
            
            if not permission:
                return ValidationResult(
                    False,
                    "Permission cannot be empty",
                    suggestions=["Provide valid permission names"]
                )
            
            # Check if permission is valid
            if not validate_permission(permission):
                return ValidationResult(
                    False,
                    f"Invalid permission: {permission}",
                    suggestions=["Use valid permission names"]
                )
        
        logger.debug("Permissions validation passed")
        return ValidationResult(True, "Permissions are valid")
        
    except Exception as e:
        logger.error(f"Error validating permissions: {e}")
        return ValidationResult(
            False,
            f"Permissions validation failed: {e}",
            suggestions=["Check permissions format and content"]
        )

def validate_system_requirements() -> ValidationResult:
    """Validate system requirements with comprehensive error handling."""
    try:
        # Check Python version
        python_version = platform.python_version()
        python_major, python_minor = map(int, python_version.split('.')[:2])
        
        if python_major < 3 or (python_major == 3 and python_minor < 8):
            return ValidationResult(
                False,
                f"Python version {python_version} is too old",
                suggestions=["Upgrade to Python 3.8 or higher"]
            )
        
        # Check memory
        try:
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            
            if memory_gb < 0.5:  # Less than 512MB
                return ValidationResult(
                    False,
                    f"Insufficient memory: {memory_gb:.2f}GB available",
                    suggestions=["Upgrade system memory to at least 512MB"]
                )
        except Exception as e:
            logger.warning(f"Could not check memory: {e}")
        
        # Check disk space
        try:
            disk = psutil.disk_usage('.')
            free_gb = disk.free / (1024**3)
            
            if free_gb < 0.1:  # Less than 100MB
                return ValidationResult(
                    False,
                    f"Insufficient disk space: {free_gb:.2f}GB available",
                    suggestions=["Free up disk space to at least 100MB"]
                )
        except Exception as e:
            logger.warning(f"Could not check disk space: {e}")
        
        logger.debug("System requirements validation passed")
        return ValidationResult(True, "System requirements are met")
        
    except Exception as e:
        logger.error(f"Error validating system requirements: {e}")
        return ValidationResult(
            False,
            f"System requirements validation failed: {e}",
            suggestions=["Check system configuration and resources"]
        )

def validate_all(data: Dict[str, Any]) -> Dict[str, ValidationResult]:
    """Validate all data with comprehensive error handling."""
    try:
        results = {}
        
        # Validate each field
        for key, value in data.items():
            try:
                if key == 'api_key':
                    results[key] = validate_api_key(value)
                elif key == 'directory':
                    results[key] = validate_directory_writable(value)
                elif key == 'disk_space':
                    results[key] = validate_disk_space(value)
                elif key == 'file_path':
                    results[key] = validate_file_path(value)
                elif key == 'json_data':
                    results[key] = validate_json_data(value)
                elif key == 'yaml_data':
                    results[key] = validate_yaml_data(value)
                elif key == 'configuration':
                    results[key] = validate_configuration(value)
                elif key == 'session_data':
                    results[key] = validate_session_data(value)
                elif key == 'workflow_data':
                    results[key] = validate_workflow_data(value)
                elif key == 'audio_file':
                    results[key] = validate_audio_file(value)
                elif key == 'video_file':
                    results[key] = validate_video_file(value)
                elif key == 'image_file':
                    results[key] = validate_image_file(value)
                elif key == 'url':
                    results[key] = validate_url(value)
                elif key == 'email':
                    results[key] = validate_email(value)
                elif key == 'phone':
                    results[key] = validate_phone_number(value)
                elif key == 'hash':
                    results[key] = validate_hash(value)
                elif key == 'permissions':
                    results[key] = validate_permissions(value)
                else:
                    # Generic validation
                    results[key] = ValidationResult(True, f"Field {key} is valid")
                    
            except Exception as e:
                logger.error(f"Error validating field {key}: {e}")
                results[key] = ValidationResult(
                    False,
                    f"Validation failed for {key}: {e}",
                    suggestions=["Check field format and content"]
                )
        
        logger.debug("All data validation completed")
        return results
        
    except Exception as e:
        logger.error(f"Error validating all data: {e}")
        return {
            'error': ValidationResult(
                False,
                f"Validation failed: {e}",
                suggestions=["Check data format and content"]
            )
        }

# Legacy functions for backward compatibility
def validate_api_key(api_key):
    """Legacy function for backward compatibility."""
    try:
        if not api_key or not isinstance(api_key, str):
            return False
        
        # Basic validation - check if it's not empty and has reasonable length
        api_key = api_key.strip()
        if len(api_key) < 10:
            return False
        
        # Check if it contains only valid characters (alphanumeric, hyphens, underscores)
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', api_key):
            return False
        
        return True
    except Exception:
        return False

def validate_directory_writable(path):
    """Legacy function for backward compatibility."""
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            path_obj.mkdir(parents=True, exist_ok=True)
        
        # Test write permission
        test_file = path_obj / ".write_test"
        try:
            test_file.write_text("test")
            test_file.unlink()
            return True
        except Exception:
            return False
    except Exception:
        return False

def validate_disk_space(path, required_gb=1):
    """Legacy function for backward compatibility."""
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            path_obj.mkdir(parents=True, exist_ok=True)
        
        disk_usage = psutil.disk_usage(str(path_obj))
        free_gb = disk_usage.free / (1024**3)
        return free_gb >= required_gb
    except Exception:
        return False

def sanitize_filename(filename):
    """Legacy function for backward compatibility."""
    try:
        if not filename:
            return "unnamed"
        
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        sanitized = filename
        for char in invalid_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Limit length
        if len(sanitized) > 255:
            sanitized = sanitized[:255]
        
        return sanitized
    except Exception:
        return "unnamed"
