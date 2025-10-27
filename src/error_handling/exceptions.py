"""Enhanced custom exception classes with comprehensive error handling."""
import traceback
from typing import Optional, Dict, Any, List
from datetime import datetime


class AGEAgentException(Exception):
    """Enhanced base exception for AGE Agent with comprehensive error handling."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None, 
                 suggestions: Optional[List[str]] = None,
                 recoverable: bool = True):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.suggestions = suggestions or []
        self.recoverable = recoverable
        self.timestamp = datetime.now()
        self.traceback = traceback.format_exc()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization."""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details,
            'suggestions': self.suggestions,
            'recoverable': self.recoverable,
            'timestamp': self.timestamp.isoformat(),
            'traceback': self.traceback
        }
    
    def get_user_message(self) -> str:
        """Get user-friendly error message."""
        msg = self.message
        if self.suggestions:
            msg += "\n\nSuggestions:\n" + "\n".join(f"• {s}" for s in self.suggestions)
        return msg


class RecordingError(AGEAgentException):
    """Enhanced exception for recording-related errors."""
    
    def __init__(self, message: str, recording_type: Optional[str] = None,
                 device_info: Optional[Dict[str, Any]] = None, **kwargs):
        suggestions = [
            "Check if recording devices are properly connected",
            "Verify recording permissions in system settings",
            "Try restarting the application",
            "Check available disk space"
        ]
        
        if recording_type == "audio":
            suggestions.extend([
                "Ensure microphone is not muted",
                "Check audio input levels",
                "Try selecting a different audio device"
            ])
        elif recording_type == "screen":
            suggestions.extend([
                "Run application as Administrator (Windows)",
                "Grant screen recording permission (macOS)",
                "Check display server permissions (Linux)"
            ])
        
        super().__init__(message, suggestions=suggestions, **kwargs)
        self.recording_type = recording_type
        self.device_info = device_info or {}


class ProcessingError(AGEAgentException):
    """Enhanced exception for data processing errors."""
    
    def __init__(self, message: str, processing_stage: Optional[str] = None,
                 data_info: Optional[Dict[str, Any]] = None, **kwargs):
        suggestions = [
            "Check if input files are valid and accessible",
            "Verify sufficient system resources (CPU, memory)",
            "Try processing smaller batches of data",
            "Check processing configuration settings"
        ]
        
        if processing_stage == "video":
            suggestions.extend([
                "Verify video file format is supported",
                "Check video file is not corrupted",
                "Ensure sufficient disk space for processing"
            ])
        elif processing_stage == "audio":
            suggestions.extend([
                "Verify audio file format is supported",
                "Check audio file is not corrupted",
                "Ensure audio transcription service is available"
            ])
        elif processing_stage == "analysis":
            suggestions.extend([
                "Check API key is valid and has sufficient quota",
                "Verify network connectivity",
                "Try reducing the amount of data being analyzed"
            ])
        
        super().__init__(message, suggestions=suggestions, **kwargs)
        self.processing_stage = processing_stage
        self.data_info = data_info or {}


class StorageError(AGEAgentException):
    """Enhanced exception for storage-related errors."""
    
    def __init__(self, message: str, storage_type: Optional[str] = None,
                 path_info: Optional[Dict[str, Any]] = None, **kwargs):
        suggestions = [
            "Check available disk space",
            "Verify file/directory permissions",
            "Ensure storage location is accessible",
            "Try cleaning up temporary files"
        ]
        
        if storage_type == "disk_space":
            suggestions.extend([
                "Free up disk space by deleting unnecessary files",
                "Move data to external storage",
                "Configure automatic cleanup settings"
            ])
        elif storage_type == "permissions":
            suggestions.extend([
                "Run application with appropriate permissions",
                "Check file/folder permissions",
                "Ensure user has write access to storage location"
            ])
        elif storage_type == "corruption":
            suggestions.extend([
                "Check file system for errors",
                "Try accessing files from different location",
                "Consider data recovery tools if critical data is lost"
            ])
        
        super().__init__(message, suggestions=suggestions, **kwargs)
        self.storage_type = storage_type
        self.path_info = path_info or {}


class LLMError(AGEAgentException):
    """Enhanced exception for LLM API errors."""
    
    def __init__(self, message: str, api_provider: Optional[str] = None,
                 api_info: Optional[Dict[str, Any]] = None, **kwargs):
        suggestions = [
            "Check API key is valid and has sufficient quota",
            "Verify network connectivity",
            "Check API service status",
            "Try reducing request size or complexity"
        ]
        
        if api_provider == "gemini":
            suggestions.extend([
                "Check Google AI Studio for API status",
                "Verify Gemini API key permissions",
                "Check rate limits and quotas"
            ])
        elif api_provider == "openai":
            suggestions.extend([
                "Check OpenAI API status page",
                "Verify OpenAI API key and billing",
                "Check rate limits and usage quotas"
            ])
        
        # Check for specific error types
        if "quota" in message.lower() or "limit" in message.lower():
            suggestions.extend([
                "Wait before making more requests",
                "Upgrade API plan if needed",
                "Implement request throttling"
            ])
        elif "network" in message.lower() or "timeout" in message.lower():
            suggestions.extend([
                "Check internet connection",
                "Try again in a few moments",
                "Check firewall/proxy settings"
            ])
        
        super().__init__(message, suggestions=suggestions, **kwargs)
        self.api_provider = api_provider
        self.api_info = api_info or {}


class ConfigurationError(AGEAgentException):
    """Enhanced exception for configuration errors."""
    
    def __init__(self, message: str, config_section: Optional[str] = None,
                 config_info: Optional[Dict[str, Any]] = None, **kwargs):
        suggestions = [
            "Check configuration file syntax",
            "Verify all required settings are present",
            "Check configuration file permissions",
            "Use default configuration as reference"
        ]
        
        if config_section == "recording":
            suggestions.extend([
                "Verify recording settings are within valid ranges",
                "Check device-specific configuration",
                "Ensure recording paths are accessible"
            ])
        elif config_section == "storage":
            suggestions.extend([
                "Verify storage paths exist and are writable",
                "Check storage size limits are reasonable",
                "Ensure backup paths are accessible"
            ])
        elif config_section == "llm":
            suggestions.extend([
                "Verify API keys are properly configured",
                "Check model names are valid",
                "Ensure API settings are within limits"
            ])
        
        super().__init__(message, suggestions=suggestions, **kwargs)
        self.config_section = config_section
        self.config_info = config_info or {}


class PermissionError(AGEAgentException):
    """Enhanced exception for permission errors."""
    
    def __init__(self, message: str, permission_type: Optional[str] = None,
                 platform_info: Optional[Dict[str, Any]] = None, **kwargs):
        suggestions = [
            "Check system permissions for the required access",
            "Run application with appropriate privileges",
            "Grant necessary permissions in system settings"
        ]
        
        if permission_type == "screen_capture":
            suggestions.extend([
                "Windows: Run as Administrator",
                "macOS: Grant screen recording permission in System Preferences",
                "Linux: Check display server permissions"
            ])
        elif permission_type == "audio_recording":
            suggestions.extend([
                "Windows: Check microphone privacy settings",
                "macOS: Grant microphone permission in System Preferences",
                "Linux: Check audio device permissions"
            ])
        elif permission_type == "file_access":
            suggestions.extend([
                "Check file/folder permissions",
                "Ensure user has read/write access",
                "Run with appropriate user privileges"
            ])
        
        super().__init__(message, suggestions=suggestions, **kwargs)
        self.permission_type = permission_type
        self.platform_info = platform_info or {}


class DeviceError(AGEAgentException):
    """Enhanced exception for device-related errors."""
    
    def __init__(self, message: str, device_type: Optional[str] = None,
                 device_info: Optional[Dict[str, Any]] = None, **kwargs):
        suggestions = [
            "Check if device is properly connected",
            "Verify device drivers are installed",
            "Try reconnecting the device",
            "Check device compatibility"
        ]
        
        if device_type == "audio":
            suggestions.extend([
                "Check audio device is not being used by another application",
                "Verify audio device is not muted",
                "Try selecting a different audio device",
                "Check audio device settings"
            ])
        elif device_type == "video":
            suggestions.extend([
                "Check monitor/display is properly connected",
                "Verify display drivers are up to date",
                "Try different display settings",
                "Check for display conflicts"
            ])
        
        super().__init__(message, suggestions=suggestions, **kwargs)
        self.device_type = device_type
        self.device_info = device_info or {}


class ValidationError(AGEAgentException):
    """Enhanced exception for data validation errors."""
    
    def __init__(self, message: str, validation_type: Optional[str] = None,
                 validation_info: Optional[Dict[str, Any]] = None, **kwargs):
        suggestions = [
            "Check input data format and structure",
            "Verify all required fields are present",
            "Ensure data values are within valid ranges",
            "Check data encoding and format"
        ]
        
        if validation_type == "file_format":
            suggestions.extend([
                "Verify file format is supported",
                "Check file is not corrupted",
                "Ensure file has proper extension"
            ])
        elif validation_type == "api_data":
            suggestions.extend([
                "Check API response format",
                "Verify required fields in response",
                "Ensure data types match expected format"
            ])
        
        super().__init__(message, suggestions=suggestions, **kwargs)
        self.validation_type = validation_type
        self.validation_info = validation_info or {}


class NetworkError(AGEAgentException):
    """Enhanced exception for network-related errors."""
    
    def __init__(self, message: str, network_type: Optional[str] = None,
                 network_info: Optional[Dict[str, Any]] = None, **kwargs):
        suggestions = [
            "Check internet connection",
            "Verify network settings",
            "Check firewall/proxy configuration",
            "Try again in a few moments"
        ]
        
        if network_type == "api_request":
            suggestions.extend([
                "Check API endpoint is accessible",
                "Verify API key and authentication",
                "Check rate limits and quotas"
            ])
        elif network_type == "download":
            suggestions.extend([
                "Check download URL is valid",
                "Verify sufficient bandwidth",
                "Try downloading from different source"
            ])
        
        super().__init__(message, suggestions=suggestions, **kwargs)
        self.network_type = network_type
        self.network_info = network_info or {}


class TimeoutError(AGEAgentException):
    """Enhanced exception for timeout errors."""
    
    def __init__(self, message: str, operation_type: Optional[str] = None,
                 timeout_info: Optional[Dict[str, Any]] = None, **kwargs):
        suggestions = [
            "Try increasing timeout settings",
            "Check system performance and resources",
            "Reduce operation complexity",
            "Try again with smaller data set"
        ]
        
        if operation_type == "api_request":
            suggestions.extend([
                "Check API service response times",
                "Verify network connectivity",
                "Consider using faster API endpoints"
            ])
        elif operation_type == "processing":
            suggestions.extend([
                "Check CPU and memory usage",
                "Reduce processing batch size",
                "Optimize processing algorithms"
            ])
        
        super().__init__(message, suggestions=suggestions, **kwargs)
        self.operation_type = operation_type
        self.timeout_info = timeout_info or {}


class ResourceError(AGEAgentException):
    """Enhanced exception for resource-related errors."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None,
                 resource_info: Optional[Dict[str, Any]] = None, **kwargs):
        suggestions = [
            "Check system resource availability",
            "Close unnecessary applications",
            "Increase system resources if possible",
            "Optimize resource usage"
        ]
        
        if resource_type == "memory":
            suggestions.extend([
                "Free up system memory",
                "Reduce memory usage in application",
                "Consider increasing system RAM"
            ])
        elif resource_type == "cpu":
            suggestions.extend([
                "Reduce CPU-intensive operations",
                "Check for background processes",
                "Consider upgrading CPU"
            ])
        elif resource_type == "disk":
            suggestions.extend([
                "Free up disk space",
                "Move data to external storage",
                "Enable automatic cleanup"
            ])
        
        super().__init__(message, suggestions=suggestions, **kwargs)
        self.resource_type = resource_type
        self.resource_info = resource_info or {}


class DependencyError(AGEAgentException):
    """Enhanced exception for dependency-related errors."""
    
    def __init__(self, message: str, dependency_name: Optional[str] = None,
                 dependency_info: Optional[Dict[str, Any]] = None, **kwargs):
        suggestions = [
            "Install missing dependencies",
            "Check dependency versions",
            "Update dependencies if needed",
            "Verify dependency compatibility"
        ]
        
        if dependency_name:
            suggestions.extend([
                f"Install {dependency_name} using package manager",
                f"Check {dependency_name} installation",
                f"Verify {dependency_name} version compatibility"
            ])
        
        super().__init__(message, suggestions=suggestions, **kwargs)
        self.dependency_name = dependency_name
        self.dependency_info = dependency_info or {}


# Exception handling utilities
def handle_exception(exc: Exception, context: Optional[str] = None) -> AGEAgentException:
    """Convert any exception to AGEAgentException with context."""
    if isinstance(exc, AGEAgentException):
        return exc
    
    # Convert built-in exceptions to appropriate AGEAgentException
    if isinstance(exc, PermissionError):
        return PermissionError(
            str(exc),
            permission_type="unknown",
            details={'original_exception': str(exc)}
        )
    elif isinstance(exc, FileNotFoundError):
        return StorageError(
            f"File not found: {str(exc)}",
            storage_type="file_access",
            details={'original_exception': str(exc)}
        )
    elif isinstance(exc, ConnectionError):
        return NetworkError(
            f"Connection error: {str(exc)}",
            network_type="connection",
            details={'original_exception': str(exc)}
        )
    elif isinstance(exc, TimeoutError):
        return TimeoutError(
            f"Operation timed out: {str(exc)}",
            operation_type="unknown",
            details={'original_exception': str(exc)}
        )
    elif isinstance(exc, ValueError):
        return ValidationError(
            f"Invalid value: {str(exc)}",
            validation_type="value",
            details={'original_exception': str(exc)}
        )
    elif isinstance(exc, ImportError):
        return DependencyError(
            f"Missing dependency: {str(exc)}",
            dependency_name=str(exc).split()[-1] if "No module named" in str(exc) else None,
            details={'original_exception': str(exc)}
        )
    else:
        # Generic AGEAgentException for unknown exceptions
        return AGEAgentException(
            f"Unexpected error: {str(exc)}",
            details={
                'original_exception': str(exc),
                'exception_type': type(exc).__name__,
                'context': context
            }
        )


def get_error_summary(exc: AGEAgentException) -> str:
    """Get a concise error summary for logging."""
    return f"{exc.__class__.__name__}: {exc.message} (Code: {exc.error_code})"


def is_recoverable_error(exc: Exception) -> bool:
    """Check if an error is recoverable."""
    if isinstance(exc, AGEAgentException):
        return exc.recoverable
    
    # Built-in exceptions that are typically recoverable
    recoverable_types = (ConnectionError, TimeoutError, PermissionError)
    return isinstance(exc, recoverable_types)
