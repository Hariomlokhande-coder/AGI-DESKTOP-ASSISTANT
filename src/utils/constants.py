"""Enhanced application constants with comprehensive validation and edge case handling."""

import os
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path

# Application Information
APP_NAME = "AGE Agent"
APP_VERSION = "1.0.0"
APP_AUTHOR = "AGE Agent Team"
APP_DESCRIPTION = "Advanced GUI Environment Agent for Desktop Automation"
APP_WEBSITE = "https://github.com/age-agent/age-agent-desktop"

# System Requirements
MIN_PYTHON_VERSION = (3, 8)
MIN_DISK_SPACE_GB = 1
MIN_MEMORY_MB = 512
MIN_CPU_CORES = 1

# Recording Constants
class RecordingConstants:
    """Recording-related constants with validation."""
    
    # FPS Settings
    MIN_FPS = 1
    MAX_FPS = 30
    DEFAULT_FPS = 1
    RECOMMENDED_FPS = 5
    
    # Duration Settings
    MIN_SESSION_DURATION = 1  # seconds
    MAX_SESSION_DURATION = 3600  # seconds (1 hour)
    DEFAULT_SESSION_DURATION = 300  # seconds (5 minutes)
    EMERGENCY_STOP_TIMEOUT = 10  # seconds
    
    # Screenshot Settings
    MIN_SCREENSHOT_INTERVAL = 1  # seconds
    MAX_SCREENSHOT_INTERVAL = 60  # seconds
    DEFAULT_SCREENSHOT_INTERVAL = 5  # seconds
    MAX_SCREENSHOTS_PER_SESSION = 1000
    
    # Frame Settings
    MIN_FRAME_WIDTH = 320
    MAX_FRAME_WIDTH = 3840
    DEFAULT_FRAME_WIDTH = 1280
    MIN_FRAME_HEIGHT = 240
    MAX_FRAME_HEIGHT = 2160
    DEFAULT_FRAME_HEIGHT = 720
    
    # Quality Settings
    MIN_QUALITY = 1
    MAX_QUALITY = 100
    DEFAULT_QUALITY = 85
    LOW_QUALITY = 60
    MEDIUM_QUALITY = 85
    HIGH_QUALITY = 95

# Audio Constants
class AudioConstants:
    """Audio-related constants with validation."""
    
    # Sample Rate Settings
    MIN_SAMPLE_RATE = 8000
    MAX_SAMPLE_RATE = 48000
    DEFAULT_SAMPLE_RATE = 16000
    RECOMMENDED_SAMPLE_RATE = 44100
    
    # Channel Settings
    MIN_CHANNELS = 1
    MAX_CHANNELS = 2
    DEFAULT_CHANNELS = 1
    
    # Chunk Size Settings
    MIN_CHUNK_SIZE = 512
    MAX_CHUNK_SIZE = 4096
    DEFAULT_CHUNK_SIZE = 1024
    
    # Audio Formats
    SUPPORTED_FORMATS = ['wav', 'mp3', 'flac', 'ogg']
    DEFAULT_FORMAT = 'wav'
    
    # Audio Quality
    LOW_AUDIO_QUALITY = 8000
    MEDIUM_AUDIO_QUALITY = 16000
    HIGH_AUDIO_QUALITY = 44100

# File Format Constants
class FileFormatConstants:
    """File format constants with validation."""
    
    # Video Formats
    SUPPORTED_VIDEO_FORMATS = ['mp4', 'avi', 'mov', 'mkv']
    DEFAULT_VIDEO_FORMAT = 'mp4'
    RECOMMENDED_VIDEO_FORMAT = 'mp4'
    
    # Audio Formats
    SUPPORTED_AUDIO_FORMATS = ['wav', 'mp3', 'flac', 'ogg']
    DEFAULT_AUDIO_FORMAT = 'wav'
    
    # Image Formats
    SUPPORTED_IMAGE_FORMATS = ['png', 'jpg', 'jpeg', 'bmp', 'tiff']
    DEFAULT_IMAGE_FORMAT = 'png'
    
    # Data Formats
    SUPPORTED_DATA_FORMATS = ['json', 'xml', 'yaml', 'csv']
    DEFAULT_DATA_FORMAT = 'json'
    
    # Compression Formats
    SUPPORTED_COMPRESSION_FORMATS = ['zip', 'tar', 'gz', 'bz2']
    DEFAULT_COMPRESSION_FORMAT = 'zip'

# Status Constants
class StatusConstants:
    """Application status constants."""
    
    # Recording Status
    STATUS_IDLE = "Idle"
    STATUS_RECORDING = "Recording..."
    STATUS_PROCESSING = "Processing..."
    STATUS_ERROR = "Error"
    STATUS_READY = "Ready"
    STATUS_INITIALIZING = "Initializing..."
    STATUS_STOPPING = "Stopping..."
    STATUS_EMERGENCY_STOP = "Emergency Stop"
    STATUS_PAUSED = "Paused"
    STATUS_COMPLETED = "Completed"
    
    # Processing Status
    STATUS_VALIDATING = "Validating..."
    STATUS_TRANSCRIBING = "Transcribing..."
    STATUS_ANALYZING = "Analyzing..."
    STATUS_GENERATING = "Generating..."
    STATUS_SAVING = "Saving..."
    STATUS_CLEANING = "Cleaning..."
    
    # Error Status
    STATUS_PERMISSION_ERROR = "Permission Error"
    STATUS_DEVICE_ERROR = "Device Error"
    STATUS_STORAGE_ERROR = "Storage Error"
    STATUS_NETWORK_ERROR = "Network Error"
    STATUS_TIMEOUT_ERROR = "Timeout Error"

# UI Constants
class UIConstants:
    """UI-related constants with validation."""
    
    # Window Settings
    MIN_WINDOW_WIDTH = 600
    MAX_WINDOW_WIDTH = 1920
    DEFAULT_WINDOW_WIDTH = 1000
    MIN_WINDOW_HEIGHT = 400
    MAX_WINDOW_HEIGHT = 1080
    DEFAULT_WINDOW_HEIGHT = 700
    
    # Button Settings
    MIN_BUTTON_HEIGHT = 30
    MAX_BUTTON_HEIGHT = 60
    DEFAULT_BUTTON_HEIGHT = 40
    MIN_BUTTON_WIDTH = 80
    MAX_BUTTON_WIDTH = 200
    DEFAULT_BUTTON_WIDTH = 120
    
    # Font Settings
    MIN_FONT_SIZE = 8
    MAX_FONT_SIZE = 24
    DEFAULT_FONT_SIZE = 12
    SUPPORTED_FONT_FAMILIES = ['Arial', 'Helvetica', 'Times New Roman', 'Courier New', 'Verdana']
    DEFAULT_FONT_FAMILY = 'Arial'
    
    # Color Settings
    PRIMARY_COLOR = "#2E86AB"
    SECONDARY_COLOR = "#A23B72"
    SUCCESS_COLOR = "#28A745"
    WARNING_COLOR = "#FFC107"
    ERROR_COLOR = "#DC3545"
    INFO_COLOR = "#17A2B8"
    
    # Theme Settings
    SUPPORTED_THEMES = ['light', 'dark', 'auto']
    DEFAULT_THEME = 'light'
    
    # Animation Settings
    DEFAULT_ANIMATION_DURATION = 300  # milliseconds
    MIN_ANIMATION_DURATION = 100
    MAX_ANIMATION_DURATION = 1000

# Storage Constants
class StorageConstants:
    """Storage-related constants with validation."""
    
    # Path Settings
    DEFAULT_BASE_PATH = "./user_data"
    DEFAULT_TEMP_PATH = "./user_data/temp"
    DEFAULT_RECORDINGS_PATH = "./user_data/recordings"
    DEFAULT_PROCESSED_PATH = "./user_data/processed"
    DEFAULT_LOGS_PATH = "./user_data/logs"
    DEFAULT_CACHE_PATH = "./user_data/cache"
    DEFAULT_BACKUP_PATH = "./user_data/backup"
    
    # Size Settings
    MIN_STORAGE_MB = 100
    MAX_STORAGE_GB = 100
    DEFAULT_MAX_STORAGE_GB = 5
    MIN_CACHE_SIZE_MB = 10
    MAX_CACHE_SIZE_MB = 1000
    DEFAULT_CACHE_SIZE_MB = 100
    
    # File Settings
    MAX_FILENAME_LENGTH = 255
    MIN_FILENAME_LENGTH = 1
    DEFAULT_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
    DEFAULT_FILENAME_PREFIX = "age_session"
    
    # Cleanup Settings
    MIN_CLEANUP_INTERVAL_HOURS = 1
    MAX_CLEANUP_INTERVAL_HOURS = 168  # 1 week
    DEFAULT_CLEANUP_INTERVAL_HOURS = 24
    MIN_BACKUP_RETENTION_DAYS = 1
    MAX_BACKUP_RETENTION_DAYS = 365
    DEFAULT_BACKUP_RETENTION_DAYS = 30

# LLM Constants
class LLMConstants:
    """LLM-related constants with validation."""
    
    # Provider Settings
    SUPPORTED_PROVIDERS = ['gemini', 'openai', 'local']
    DEFAULT_PROVIDER = 'gemini'
    
    # Model Settings
    GEMINI_MODELS = ['gemini-2.0-flash-exp', 'gemini-1.5-pro', 'gemini-1.5-flash']
    OPENAI_MODELS = ['gpt-4', 'gpt-3.5-turbo', 'gpt-4-turbo']
    DEFAULT_MODEL = 'gemini-2.0-flash-exp'
    
    # API Settings
    MIN_TEMPERATURE = 0.0
    MAX_TEMPERATURE = 2.0
    DEFAULT_TEMPERATURE = 0.3
    MIN_MAX_TOKENS = 100
    MAX_MAX_TOKENS = 8000
    DEFAULT_MAX_TOKENS = 2000
    
    # Rate Limiting
    MIN_REQUESTS_PER_MINUTE = 1
    MAX_REQUESTS_PER_MINUTE = 1000
    DEFAULT_REQUESTS_PER_MINUTE = 60
    MIN_REQUESTS_PER_HOUR = 1
    MAX_REQUESTS_PER_HOUR = 10000
    DEFAULT_REQUESTS_PER_HOUR = 1000
    
    # Timeout Settings
    MIN_TIMEOUT_SECONDS = 5
    MAX_TIMEOUT_SECONDS = 300
    DEFAULT_TIMEOUT_SECONDS = 30
    
    # Retry Settings
    MIN_MAX_RETRIES = 0
    MAX_MAX_RETRIES = 10
    DEFAULT_MAX_RETRIES = 3
    MIN_RETRY_DELAY_SECONDS = 0.1
    MAX_RETRY_DELAY_SECONDS = 60
    DEFAULT_RETRY_DELAY_SECONDS = 1

# Performance Constants
class PerformanceConstants:
    """Performance-related constants with validation."""
    
    # Resource Limits
    MIN_MEMORY_LIMIT_MB = 256
    MAX_MEMORY_LIMIT_MB = 8192
    DEFAULT_MEMORY_LIMIT_MB = 1024
    MIN_CPU_LIMIT_PERCENT = 10
    MAX_CPU_LIMIT_PERCENT = 100
    DEFAULT_CPU_LIMIT_PERCENT = 80
    
    # Worker Settings
    MIN_MAX_WORKERS = 1
    MAX_MAX_WORKERS = 16
    DEFAULT_MAX_WORKERS = 4
    
    # Processing Settings
    MIN_PROCESSING_TIMEOUT_SECONDS = 30
    MAX_PROCESSING_TIMEOUT_SECONDS = 1800  # 30 minutes
    DEFAULT_PROCESSING_TIMEOUT_SECONDS = 300  # 5 minutes
    
    # Cache Settings
    MIN_CACHE_SIZE_MB = 10
    MAX_CACHE_SIZE_MB = 1000
    DEFAULT_CACHE_SIZE_MB = 100

# Security Constants
class SecurityConstants:
    """Security-related constants."""
    
    # Encryption Settings
    SUPPORTED_ENCRYPTION_ALGORITHMS = ['AES-256', 'AES-128', 'ChaCha20']
    DEFAULT_ENCRYPTION_ALGORITHM = 'AES-256'
    MIN_KEY_LENGTH = 128
    MAX_KEY_LENGTH = 512
    DEFAULT_KEY_LENGTH = 256
    
    # Privacy Settings
    SUPPORTED_BLUR_LEVELS = ['low', 'medium', 'high']
    DEFAULT_BLUR_LEVEL = 'medium'
    MIN_BLUR_RADIUS = 1
    MAX_BLUR_RADIUS = 20
    DEFAULT_BLUR_RADIUS = 5
    
    # Permission Settings
    REQUIRED_PERMISSIONS = ['screen_capture', 'audio_recording', 'file_access']
    OPTIONAL_PERMISSIONS = ['network_access', 'system_monitoring']

# Error Constants
class ErrorConstants:
    """Error-related constants."""
    
    # Error Codes
    ERROR_CODES = {
        'RECORDING_ERROR': 'REC001',
        'PROCESSING_ERROR': 'PROC001',
        'STORAGE_ERROR': 'STOR001',
        'LLM_ERROR': 'LLM001',
        'CONFIGURATION_ERROR': 'CONF001',
        'PERMISSION_ERROR': 'PERM001',
        'DEVICE_ERROR': 'DEV001',
        'VALIDATION_ERROR': 'VAL001',
        'NETWORK_ERROR': 'NET001',
        'TIMEOUT_ERROR': 'TIME001',
        'RESOURCE_ERROR': 'RES001',
        'DEPENDENCY_ERROR': 'DEP001'
    }
    
    # Error Messages
    ERROR_MESSAGES = {
        'RECORDING_ERROR': 'Recording operation failed',
        'PROCESSING_ERROR': 'Processing operation failed',
        'STORAGE_ERROR': 'Storage operation failed',
        'LLM_ERROR': 'LLM operation failed',
        'CONFIGURATION_ERROR': 'Configuration error',
        'PERMISSION_ERROR': 'Permission denied',
        'DEVICE_ERROR': 'Device operation failed',
        'VALIDATION_ERROR': 'Validation failed',
        'NETWORK_ERROR': 'Network operation failed',
        'TIMEOUT_ERROR': 'Operation timed out',
        'RESOURCE_ERROR': 'Insufficient resources',
        'DEPENDENCY_ERROR': 'Missing dependency'
    }

# Validation Functions
def validate_fps(fps: int) -> bool:
    """Validate FPS value."""
    return RecordingConstants.MIN_FPS <= fps <= RecordingConstants.MAX_FPS

def validate_sample_rate(sample_rate: int) -> bool:
    """Validate audio sample rate."""
    return AudioConstants.MIN_SAMPLE_RATE <= sample_rate <= AudioConstants.MAX_SAMPLE_RATE

def validate_window_size(width: int, height: int) -> bool:
    """Validate window dimensions."""
    return (UIConstants.MIN_WINDOW_WIDTH <= width <= UIConstants.MAX_WINDOW_WIDTH and
            UIConstants.MIN_WINDOW_HEIGHT <= height <= UIConstants.MAX_WINDOW_HEIGHT)

def validate_temperature(temperature: float) -> bool:
    """Validate LLM temperature."""
    return LLMConstants.MIN_TEMPERATURE <= temperature <= LLMConstants.MAX_TEMPERATURE

def validate_memory_limit(memory_mb: int) -> bool:
    """Validate memory limit."""
    return PerformanceConstants.MIN_MEMORY_LIMIT_MB <= memory_mb <= PerformanceConstants.MAX_MEMORY_LIMIT_MB

def validate_file_format(format_name: str, format_type: str) -> bool:
    """Validate file format."""
    if format_type == 'video':
        return format_name.lower() in FileFormatConstants.SUPPORTED_VIDEO_FORMATS
    elif format_type == 'audio':
        return format_name.lower() in FileFormatConstants.SUPPORTED_AUDIO_FORMATS
    elif format_type == 'image':
        return format_name.lower() in FileFormatConstants.SUPPORTED_IMAGE_FORMATS
    elif format_type == 'data':
        return format_name.lower() in FileFormatConstants.SUPPORTED_DATA_FORMATS
    return False

def validate_theme(theme: str) -> bool:
    """Validate UI theme."""
    return theme.lower() in UIConstants.SUPPORTED_THEMES

def validate_provider(provider: str) -> bool:
    """Validate LLM provider."""
    return provider.lower() in LLMConstants.SUPPORTED_PROVIDERS

def validate_model(model: str, provider: str) -> bool:
    """Validate LLM model for provider."""
    if provider.lower() == 'gemini':
        return model in LLMConstants.GEMINI_MODELS
    elif provider.lower() == 'openai':
        return model in LLMConstants.OPENAI_MODELS
    return False

def validate_storage_path(path: str) -> bool:
    """Validate storage path."""
    try:
        path_obj = Path(path)
        return path_obj.is_absolute() or path_obj.resolve().exists() or path_obj.parent.exists()
    except Exception:
        return False

def validate_filename(filename: str) -> bool:
    """Validate filename."""
    if not filename:
        return False
    if len(filename) < StorageConstants.MIN_FILENAME_LENGTH:
        return False
    if len(filename) > StorageConstants.MAX_FILENAME_LENGTH:
        return False
    # Check for invalid characters
    invalid_chars = '<>:"/\\|?*'
    return not any(char in filename for char in invalid_chars)

def validate_duration(duration: int) -> bool:
    """Validate session duration."""
    return RecordingConstants.MIN_SESSION_DURATION <= duration <= RecordingConstants.MAX_SESSION_DURATION

def validate_quality(quality: int) -> bool:
    """Validate quality setting."""
    return RecordingConstants.MIN_QUALITY <= quality <= RecordingConstants.MAX_QUALITY

def validate_chunk_size(chunk_size: int) -> bool:
    """Validate audio chunk size."""
    return AudioConstants.MIN_CHUNK_SIZE <= chunk_size <= AudioConstants.MAX_CHUNK_SIZE

def validate_channels(channels: int) -> bool:
    """Validate audio channels."""
    return AudioConstants.MIN_CHANNELS <= channels <= AudioConstants.MAX_CHANNELS

def validate_max_tokens(max_tokens: int) -> bool:
    """Validate max tokens."""
    return LLMConstants.MIN_MAX_TOKENS <= max_tokens <= LLMConstants.MAX_MAX_TOKENS

def validate_timeout(timeout: int) -> bool:
    """Validate timeout value."""
    return LLMConstants.MIN_TIMEOUT_SECONDS <= timeout <= LLMConstants.MAX_TIMEOUT_SECONDS

def validate_max_retries(max_retries: int) -> bool:
    """Validate max retries."""
    return LLMConstants.MIN_MAX_RETRIES <= max_retries <= LLMConstants.MAX_MAX_RETRIES

def validate_retry_delay(retry_delay: float) -> bool:
    """Validate retry delay."""
    return LLMConstants.MIN_RETRY_DELAY_SECONDS <= retry_delay <= LLMConstants.MAX_RETRY_DELAY_SECONDS

def validate_requests_per_minute(requests: int) -> bool:
    """Validate requests per minute."""
    return LLMConstants.MIN_REQUESTS_PER_MINUTE <= requests <= LLMConstants.MAX_REQUESTS_PER_MINUTE

def validate_requests_per_hour(requests: int) -> bool:
    """Validate requests per hour."""
    return LLMConstants.MIN_REQUESTS_PER_HOUR <= requests <= LLMConstants.MAX_REQUESTS_PER_HOUR

def validate_memory_limit(memory_mb: int) -> bool:
    """Validate memory limit."""
    return PerformanceConstants.MIN_MEMORY_LIMIT_MB <= memory_mb <= PerformanceConstants.MAX_MEMORY_LIMIT_MB

def validate_cpu_limit(cpu_percent: int) -> bool:
    """Validate CPU limit."""
    return PerformanceConstants.MIN_CPU_LIMIT_PERCENT <= cpu_percent <= PerformanceConstants.MAX_CPU_LIMIT_PERCENT

def validate_max_workers(max_workers: int) -> bool:
    """Validate max workers."""
    return PerformanceConstants.MIN_MAX_WORKERS <= max_workers <= PerformanceConstants.MAX_MAX_WORKERS

def validate_processing_timeout(timeout: int) -> bool:
    """Validate processing timeout."""
    return PerformanceConstants.MIN_PROCESSING_TIMEOUT_SECONDS <= timeout <= PerformanceConstants.MAX_PROCESSING_TIMEOUT_SECONDS

def validate_cache_size(cache_mb: int) -> bool:
    """Validate cache size."""
    return PerformanceConstants.MIN_CACHE_SIZE_MB <= cache_mb <= PerformanceConstants.MAX_CACHE_SIZE_MB

def validate_storage_size(storage_gb: int) -> bool:
    """Validate storage size."""
    return StorageConstants.MIN_STORAGE_MB <= storage_gb * 1024 <= StorageConstants.MAX_STORAGE_GB * 1024

def validate_cleanup_interval(interval_hours: int) -> bool:
    """Validate cleanup interval."""
    return StorageConstants.MIN_CLEANUP_INTERVAL_HOURS <= interval_hours <= StorageConstants.MAX_CLEANUP_INTERVAL_HOURS

def validate_backup_retention(retention_days: int) -> bool:
    """Validate backup retention."""
    return StorageConstants.MIN_BACKUP_RETENTION_DAYS <= retention_days <= StorageConstants.MAX_BACKUP_RETENTION_DAYS

def validate_font_size(font_size: int) -> bool:
    """Validate font size."""
    return UIConstants.MIN_FONT_SIZE <= font_size <= UIConstants.MAX_FONT_SIZE

def validate_font_family(font_family: str) -> bool:
    """Validate font family."""
    return font_family in UIConstants.SUPPORTED_FONT_FAMILIES

def validate_animation_duration(duration: int) -> bool:
    """Validate animation duration."""
    return UIConstants.MIN_ANIMATION_DURATION <= duration <= UIConstants.MAX_ANIMATION_DURATION

def validate_blur_radius(radius: int) -> bool:
    """Validate blur radius."""
    return SecurityConstants.MIN_BLUR_RADIUS <= radius <= SecurityConstants.MAX_BLUR_RADIUS

def validate_blur_level(level: str) -> bool:
    """Validate blur level."""
    return level.lower() in SecurityConstants.SUPPORTED_BLUR_LEVELS

def validate_encryption_algorithm(algorithm: str) -> bool:
    """Validate encryption algorithm."""
    return algorithm in SecurityConstants.SUPPORTED_ENCRYPTION_ALGORITHMS

def validate_key_length(key_length: int) -> bool:
    """Validate encryption key length."""
    return SecurityConstants.MIN_KEY_LENGTH <= key_length <= SecurityConstants.MAX_KEY_LENGTH

def validate_permission(permission: str) -> bool:
    """Validate permission type."""
    return permission in SecurityConstants.REQUIRED_PERMISSIONS or permission in SecurityConstants.OPTIONAL_PERMISSIONS

# Utility Functions
def get_default_config() -> Dict[str, Any]:
    """Get default configuration values."""
    return {
        'recording': {
            'fps': RecordingConstants.DEFAULT_FPS,
            'screenshot_interval_seconds': RecordingConstants.DEFAULT_SCREENSHOT_INTERVAL,
            'max_duration_minutes': RecordingConstants.MAX_SESSION_DURATION // 60,
            'frame_width': RecordingConstants.DEFAULT_FRAME_WIDTH,
            'frame_height': RecordingConstants.DEFAULT_FRAME_HEIGHT,
            'quality': RecordingConstants.DEFAULT_QUALITY
        },
        'audio': {
            'sample_rate': AudioConstants.DEFAULT_SAMPLE_RATE,
            'channels': AudioConstants.DEFAULT_CHANNELS,
            'chunk_size': AudioConstants.DEFAULT_CHUNK_SIZE,
            'format': AudioConstants.DEFAULT_FORMAT
        },
        'ui': {
            'window_width': UIConstants.DEFAULT_WINDOW_WIDTH,
            'window_height': UIConstants.DEFAULT_WINDOW_HEIGHT,
            'font_size': UIConstants.DEFAULT_FONT_SIZE,
            'font_family': UIConstants.DEFAULT_FONT_FAMILY,
            'theme': UIConstants.DEFAULT_THEME
        },
        'storage': {
            'base_path': StorageConstants.DEFAULT_BASE_PATH,
            'temp_path': StorageConstants.DEFAULT_TEMP_PATH,
            'recordings_path': StorageConstants.DEFAULT_RECORDINGS_PATH,
            'processed_path': StorageConstants.DEFAULT_PROCESSED_PATH,
            'logs_path': StorageConstants.DEFAULT_LOGS_PATH,
            'cache_path': StorageConstants.DEFAULT_CACHE_PATH,
            'max_storage_gb': StorageConstants.DEFAULT_MAX_STORAGE_GB,
            'cache_size_mb': StorageConstants.DEFAULT_CACHE_SIZE_MB
        },
        'llm': {
            'provider': LLMConstants.DEFAULT_PROVIDER,
            'model': LLMConstants.DEFAULT_MODEL,
            'temperature': LLMConstants.DEFAULT_TEMPERATURE,
            'max_tokens': LLMConstants.DEFAULT_MAX_TOKENS,
            'timeout_seconds': LLMConstants.DEFAULT_TIMEOUT_SECONDS,
            'max_retries': LLMConstants.DEFAULT_MAX_RETRIES,
            'retry_delay_seconds': LLMConstants.DEFAULT_RETRY_DELAY_SECONDS,
            'requests_per_minute': LLMConstants.DEFAULT_REQUESTS_PER_MINUTE,
            'requests_per_hour': LLMConstants.DEFAULT_REQUESTS_PER_HOUR
        },
        'performance': {
            'memory_limit_mb': PerformanceConstants.DEFAULT_MEMORY_LIMIT_MB,
            'cpu_limit_percent': PerformanceConstants.DEFAULT_CPU_LIMIT_PERCENT,
            'max_workers': PerformanceConstants.DEFAULT_MAX_WORKERS,
            'processing_timeout_seconds': PerformanceConstants.DEFAULT_PROCESSING_TIMEOUT_SECONDS,
            'cache_size_mb': PerformanceConstants.DEFAULT_CACHE_SIZE_MB
        },
        'security': {
            'encryption_algorithm': SecurityConstants.DEFAULT_ENCRYPTION_ALGORITHM,
            'key_length': SecurityConstants.DEFAULT_KEY_LENGTH,
            'blur_level': SecurityConstants.DEFAULT_BLUR_LEVEL,
            'blur_radius': SecurityConstants.DEFAULT_BLUR_RADIUS
        }
    }

def get_system_info() -> Dict[str, Any]:
    """Get system information."""
    try:
        import platform
        import psutil
        
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'disk_total_gb': round(psutil.disk_usage('.').total / (1024**3), 2),
            'disk_free_gb': round(psutil.disk_usage('.').free / (1024**3), 2)
        }
    except Exception:
        return {
            'platform': 'Unknown',
            'platform_version': 'Unknown',
            'architecture': 'Unknown',
            'processor': 'Unknown',
            'python_version': 'Unknown',
            'cpu_count': 1,
            'memory_total_gb': 0,
            'disk_total_gb': 0,
            'disk_free_gb': 0
        }

def check_system_requirements() -> Dict[str, bool]:
    """Check if system meets requirements."""
    try:
        import psutil
        
        # Check Python version
        python_ok = sys.version_info >= MIN_PYTHON_VERSION
        
        # Check memory
        memory_gb = psutil.virtual_memory().total / (1024**3)
        memory_ok = memory_gb >= MIN_MEMORY_MB / 1024
        
        # Check disk space
        disk_gb = psutil.disk_usage('.').free / (1024**3)
        disk_ok = disk_gb >= MIN_DISK_SPACE_GB
        
        # Check CPU cores
        cpu_ok = psutil.cpu_count() >= MIN_CPU_CORES
        
        return {
            'python_version': python_ok,
            'memory': memory_ok,
            'disk_space': disk_ok,
            'cpu_cores': cpu_ok,
            'overall': python_ok and memory_ok and disk_ok and cpu_ok
        }
    except Exception:
        return {
            'python_version': False,
            'memory': False,
            'disk_space': False,
            'cpu_cores': False,
            'overall': False
        }

def get_error_code(error_type: str) -> str:
    """Get error code for error type."""
    return ErrorConstants.ERROR_CODES.get(error_type, 'UNKNOWN')

def get_error_message(error_type: str) -> str:
    """Get error message for error type."""
    return ErrorConstants.ERROR_MESSAGES.get(error_type, 'Unknown error')

def get_supported_formats(format_type: str) -> List[str]:
    """Get supported formats for type."""
    if format_type == 'video':
        return FileFormatConstants.SUPPORTED_VIDEO_FORMATS
    elif format_type == 'audio':
        return FileFormatConstants.SUPPORTED_AUDIO_FORMATS
    elif format_type == 'image':
        return FileFormatConstants.SUPPORTED_IMAGE_FORMATS
    elif format_type == 'data':
        return FileFormatConstants.SUPPORTED_DATA_FORMATS
    elif format_type == 'compression':
        return FileFormatConstants.SUPPORTED_COMPRESSION_FORMATS
    return []

def get_recommended_settings() -> Dict[str, Any]:
    """Get recommended settings for optimal performance."""
    return {
        'recording': {
            'fps': RecordingConstants.RECOMMENDED_FPS,
            'quality': RecordingConstants.MEDIUM_QUALITY,
            'screenshot_interval_seconds': RecordingConstants.DEFAULT_SCREENSHOT_INTERVAL
        },
        'audio': {
            'sample_rate': AudioConstants.RECOMMENDED_SAMPLE_RATE,
            'channels': AudioConstants.DEFAULT_CHANNELS,
            'format': AudioConstants.DEFAULT_FORMAT
        },
        'ui': {
            'theme': UIConstants.DEFAULT_THEME,
            'font_size': UIConstants.DEFAULT_FONT_SIZE,
            'font_family': UIConstants.DEFAULT_FONT_FAMILY
        },
        'performance': {
            'max_workers': min(PerformanceConstants.DEFAULT_MAX_WORKERS, psutil.cpu_count()),
            'memory_limit_mb': min(PerformanceConstants.DEFAULT_MEMORY_LIMIT_MB, 
                                 int(psutil.virtual_memory().total / (1024**2) * 0.1)),
            'cache_size_mb': PerformanceConstants.DEFAULT_CACHE_SIZE_MB
        }
    }

# Legacy constants for backward compatibility
DEFAULT_FPS = RecordingConstants.DEFAULT_FPS
DEFAULT_SCREENSHOT_INTERVAL = RecordingConstants.DEFAULT_SCREENSHOT_INTERVAL
MAX_SESSION_DURATION = RecordingConstants.MAX_SESSION_DURATION
VIDEO_FORMAT = FileFormatConstants.DEFAULT_VIDEO_FORMAT
AUDIO_FORMAT = FileFormatConstants.DEFAULT_AUDIO_FORMAT
JSON_FORMAT = FileFormatConstants.DEFAULT_DATA_FORMAT
STATUS_IDLE = StatusConstants.STATUS_IDLE
STATUS_RECORDING = StatusConstants.STATUS_RECORDING
STATUS_PROCESSING = StatusConstants.STATUS_PROCESSING
STATUS_ERROR = StatusConstants.STATUS_ERROR
STATUS_READY = StatusConstants.STATUS_READY
WINDOW_WIDTH = UIConstants.DEFAULT_WINDOW_WIDTH
WINDOW_HEIGHT = UIConstants.DEFAULT_WINDOW_HEIGHT
BUTTON_HEIGHT = UIConstants.DEFAULT_BUTTON_HEIGHT
