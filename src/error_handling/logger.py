"""Enhanced logging and error handling with comprehensive features."""
import logging
import logging.handlers
import os
import sys
import traceback
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
import threading
from collections import deque
from .exceptions import AGEAgentException, handle_exception


class AGELogger:
    """Enhanced custom logger for AGE Agent with comprehensive features."""
    
    def __init__(self, log_dir: str = "logs", max_log_files: int = 10, 
                 max_log_size_mb: int = 10, log_level: str = "INFO",
                 enable_console: bool = True, enable_file: bool = True,
                 enable_json_logs: bool = False):
        self.log_dir = Path(log_dir)
        self.max_log_files = max_log_files
        self.max_log_size_mb = max_log_size_mb
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.enable_json_logs = enable_json_logs
        
        # Create log directory
        self._ensure_log_directory()
        
        # Initialize logger
        self.logger = logging.getLogger("AGEAgent")
        self.logger.setLevel(self._get_log_level(log_level))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Add handlers
        if self.enable_file:
            self._setup_file_handler()
        
        if self.enable_console:
            self._setup_console_handler()
        
        # Initialize log buffer for recent logs
        self.log_buffer = deque(maxlen=1000)
        self.buffer_lock = threading.Lock()
        
        # Performance tracking
        self.log_counts = {
            'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 
            'ERROR': 0, 'CRITICAL': 0
        }
        self.start_time = datetime.now()
        
        # Log rotation tracking
        self.current_log_file = None
        self.last_rotation_check = datetime.now()
        
        # Error tracking
        self.error_count = 0
        self.critical_count = 0
        
        # Log initial startup
        self.info("AGE Agent Logger initialized", extra={
            'log_dir': str(self.log_dir),
            'max_files': self.max_log_files,
            'max_size_mb': self.max_log_size_mb,
            'log_level': log_level
        })
    
    def _ensure_log_directory(self) -> None:
        """Ensure log directory exists and is writable."""
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            
            # Test write permissions
            test_file = self.log_dir / ".test_write"
            test_file.write_text("test")
            test_file.unlink()
            
        except Exception as e:
            # Fallback to current directory
            self.log_dir = Path(".")
            print(f"Warning: Could not create log directory, using current directory: {e}")
    
    def _get_log_level(self, level_str: str) -> int:
        """Convert string log level to logging constant."""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return level_map.get(level_str.upper(), logging.INFO)
    
    def _setup_file_handler(self) -> None:
        """Setup rotating file handler."""
        try:
            # Create rotating file handler
            log_file = self.log_dir / f"age_agent_{datetime.now().strftime('%Y%m%d')}.log"
            self.current_log_file = log_file
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self.max_log_size_mb * 1024 * 1024,  # Convert MB to bytes
                backupCount=self.max_log_files - 1,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            
            # Create formatter
            if self.enable_json_logs:
                formatter = self._create_json_formatter()
            else:
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            print(f"Warning: Could not setup file logging: {e}")
    
    def _setup_console_handler(self) -> None:
        """Setup console handler."""
        try:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            # Create colored formatter for console
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
        except Exception as e:
            print(f"Warning: Could not setup console logging: {e}")
    
    def _create_json_formatter(self) -> logging.Formatter:
        """Create JSON formatter for structured logging."""
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                    'level': record.levelname,
                    'logger': record.name,
                    'message': record.getMessage(),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno
                }
                
                # Add extra fields if present
                if hasattr(record, 'extra') and record.extra:
                    log_entry.update(record.extra)
                
                # Add exception info if present
                if record.exc_info:
                    log_entry['exception'] = self.formatException(record.exc_info)
                
                return json.dumps(log_entry, ensure_ascii=False)
        
        return JSONFormatter()
    
    def _check_log_rotation(self) -> None:
        """Check if log rotation is needed."""
        try:
            current_time = datetime.now()
            if (current_time - self.last_rotation_check).seconds < 3600:  # Check every hour
                return
            
            self.last_rotation_check = current_time
            
            # Check if current log file is too large
            if self.current_log_file and self.current_log_file.exists():
                file_size = self.current_log_file.stat().st_size
                max_size = self.max_log_size_mb * 1024 * 1024
                
                if file_size > max_size:
                    self.info("Log rotation triggered by file size")
                    # The RotatingFileHandler will handle the rotation
            
            # Clean up old log files
            self._cleanup_old_logs()
            
        except Exception as e:
            print(f"Error during log rotation check: {e}")
    
    def _cleanup_old_logs(self) -> None:
        """Clean up old log files beyond the retention limit."""
        try:
            log_files = list(self.log_dir.glob("age_agent_*.log*"))
            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Keep only the most recent files
            files_to_remove = log_files[self.max_log_files:]
            for file_path in files_to_remove:
                try:
                    file_path.unlink()
                    self.debug(f"Removed old log file: {file_path}")
                except Exception as e:
                    self.warning(f"Could not remove old log file {file_path}: {e}")
                    
        except Exception as e:
            print(f"Error cleaning up old logs: {e}")
    
    def _log_with_buffer(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log message and add to buffer."""
        try:
            # Add to buffer
            with self.buffer_lock:
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'level': level,
                    'message': message,
                    'extra': extra or {}
                }
                self.log_buffer.append(log_entry)
            
            # Update counters
            self.log_counts[level] += 1
            
            # Track errors
            if level in ['ERROR', 'CRITICAL']:
                self.error_count += 1
                if level == 'CRITICAL':
                    self.critical_count += 1
            
            # Check log rotation periodically
            self._check_log_rotation()
            
        except Exception as e:
            print(f"Error in log buffer: {e}")
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """Log debug message."""
        try:
            self._log_with_buffer('DEBUG', message, extra)
            self.logger.debug(message, extra=extra, exc_info=exc_info)
        except Exception as e:
            print(f"Debug logging error: {e}")
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """Log info message."""
        try:
            self._log_with_buffer('INFO', message, extra)
            self.logger.info(message, extra=extra, exc_info=exc_info)
        except Exception as e:
            print(f"Info logging error: {e}")
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """Log warning message."""
        try:
            self._log_with_buffer('WARNING', message, extra)
            self.logger.warning(message, extra=extra, exc_info=exc_info)
        except Exception as e:
            print(f"Warning logging error: {e}")
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """Log error message."""
        try:
            self._log_with_buffer('ERROR', message, extra)
            self.logger.error(message, extra=extra, exc_info=exc_info)
        except Exception as e:
            print(f"Error logging error: {e}")
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """Log critical message."""
        try:
            self._log_with_buffer('CRITICAL', message, extra)
            self.logger.critical(message, extra=extra, exc_info=exc_info)
        except Exception as e:
            print(f"Critical logging error: {e}")
    
    def exception(self, message: str, exc: Optional[Exception] = None, 
                 extra: Optional[Dict[str, Any]] = None) -> None:
        """Log exception with full traceback."""
        try:
            if exc:
                # Convert to AGEAgentException if needed
                if not isinstance(exc, AGEAgentException):
                    exc = handle_exception(exc, context=message)
                
                # Add exception details to extra
                if extra is None:
                    extra = {}
                extra.update({
                    'exception_type': type(exc).__name__,
                    'exception_code': getattr(exc, 'error_code', None),
                    'recoverable': getattr(exc, 'recoverable', True),
                    'suggestions': getattr(exc, 'suggestions', [])
                })
                
                message = f"{message}: {exc.message}"
            
            self.error(message, extra=extra, exc_info=True)
            
        except Exception as e:
            print(f"Exception logging error: {e}")
    
    def log_performance(self, operation: str, duration: float, 
                       details: Optional[Dict[str, Any]] = None) -> None:
        """Log performance metrics."""
        try:
            extra = {
                'operation': operation,
                'duration_ms': round(duration * 1000, 2),
                'performance_log': True
            }
            if details:
                extra.update(details)
            
            self.info(f"Performance: {operation} took {duration:.3f}s", extra=extra)
            
        except Exception as e:
            print(f"Performance logging error: {e}")
    
    def log_system_info(self) -> None:
        """Log system information."""
        try:
            import platform
            import psutil
            
            system_info = {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'architecture': platform.architecture()[0],
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'disk_total_gb': round(psutil.disk_usage('/').total / (1024**3), 2) if platform.system() != 'Windows' else round(psutil.disk_usage('C:').total / (1024**3), 2)
            }
            
            self.info("System Information", extra={'system_info': system_info})
            
        except Exception as e:
            self.warning(f"Could not log system info: {e}")
    
    def get_recent_logs(self, count: int = 100, level: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent log entries from buffer."""
        try:
            with self.buffer_lock:
                logs = list(self.log_buffer)
            
            if level:
                logs = [log for log in logs if log['level'] == level.upper()]
            
            return logs[-count:] if count > 0 else logs
            
        except Exception as e:
            print(f"Error getting recent logs: {e}")
            return []
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get logging statistics."""
        try:
            uptime = datetime.now() - self.start_time
            
            return {
                'uptime_seconds': uptime.total_seconds(),
                'uptime_formatted': str(uptime).split('.')[0],
                'log_counts': self.log_counts.copy(),
                'error_count': self.error_count,
                'critical_count': self.critical_count,
                'buffer_size': len(self.log_buffer),
                'log_dir': str(self.log_dir),
                'current_log_file': str(self.current_log_file) if self.current_log_file else None,
                'max_log_files': self.max_log_files,
                'max_log_size_mb': self.max_log_size_mb
            }
            
        except Exception as e:
            print(f"Error getting log statistics: {e}")
            return {}
    
    def export_logs(self, output_file: str, level: Optional[str] = None, 
                   start_time: Optional[datetime] = None, 
                   end_time: Optional[datetime] = None) -> bool:
        """Export logs to file."""
        try:
            logs = self.get_recent_logs(count=0, level=level)
            
            # Filter by time if specified
            if start_time or end_time:
                filtered_logs = []
                for log in logs:
                    log_time = datetime.fromisoformat(log['timestamp'])
                    if start_time and log_time < start_time:
                        continue
                    if end_time and log_time > end_time:
                        continue
                    filtered_logs.append(log)
                logs = filtered_logs
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                if self.enable_json_logs:
                    json.dump(logs, f, indent=2, ensure_ascii=False)
                else:
                    for log in logs:
                        f.write(f"{log['timestamp']} - {log['level']} - {log['message']}\n")
            
            self.info(f"Exported {len(logs)} log entries to {output_file}")
            return True
            
        except Exception as e:
            self.error(f"Error exporting logs: {e}")
            return False
    
    def clear_logs(self) -> None:
        """Clear log buffer."""
        try:
            with self.buffer_lock:
                self.log_buffer.clear()
            self.info("Log buffer cleared")
        except Exception as e:
            print(f"Error clearing logs: {e}")
    
    def set_log_level(self, level: str) -> None:
        """Change log level dynamically."""
        try:
            new_level = self._get_log_level(level)
            self.logger.setLevel(new_level)
            
            # Update console handler level
            for handler in self.logger.handlers:
                if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                    handler.setLevel(new_level)
            
            self.info(f"Log level changed to {level}")
            
        except Exception as e:
            print(f"Error changing log level: {e}")
    
    def shutdown(self) -> None:
        """Shutdown logger and cleanup resources."""
        try:
            # Log shutdown
            self.info("Logger shutting down")
            
            # Export final statistics
            stats = self.get_log_statistics()
            self.info("Final log statistics", extra={'final_stats': stats})
            
            # Close all handlers
            for handler in self.logger.handlers:
                handler.close()
                self.logger.removeHandler(handler)
            
        except Exception as e:
            print(f"Error during logger shutdown: {e}")


# Global logger instance with enhanced configuration
def create_logger(log_dir: str = "logs", **kwargs) -> AGELogger:
    """Create a new logger instance with custom configuration."""
    return AGELogger(log_dir=log_dir, **kwargs)


# Default global logger instance
logger = AGELogger()


# Convenience functions for common logging patterns
def log_function_call(func_name: str, args: Optional[Dict[str, Any]] = None, 
                     kwargs: Optional[Dict[str, Any]] = None) -> None:
    """Log function call with parameters."""
    extra = {
        'function_call': True,
        'function_name': func_name,
        'args': args or {},
        'kwargs': kwargs or {}
    }
    logger.debug(f"Calling function: {func_name}", extra=extra)


def log_function_result(func_name: str, result: Any, duration: Optional[float] = None) -> None:
    """Log function result."""
    extra = {
        'function_result': True,
        'function_name': func_name,
        'result_type': type(result).__name__
    }
    if duration is not None:
        extra['duration_ms'] = round(duration * 1000, 2)
    
    logger.debug(f"Function {func_name} completed", extra=extra)


def log_api_call(api_name: str, endpoint: str, method: str = "GET", 
                status_code: Optional[int] = None, duration: Optional[float] = None) -> None:
    """Log API call details."""
    extra = {
        'api_call': True,
        'api_name': api_name,
        'endpoint': endpoint,
        'method': method,
        'status_code': status_code,
        'duration_ms': round(duration * 1000, 2) if duration else None
    }
    
    level = 'info' if status_code and status_code < 400 else 'warning'
    message = f"API call: {method} {endpoint}"
    if status_code:
        message += f" -> {status_code}"
    
    getattr(logger, level)(message, extra=extra)


def log_user_action(action: str, details: Optional[Dict[str, Any]] = None) -> None:
    """Log user actions."""
    extra = {
        'user_action': True,
        'action': action,
        'details': details or {}
    }
    logger.info(f"User action: {action}", extra=extra)


def log_system_event(event: str, details: Optional[Dict[str, Any]] = None) -> None:
    """Log system events."""
    extra = {
        'system_event': True,
        'event': event,
        'details': details or {}
    }
    logger.info(f"System event: {event}", extra=extra)
