"""Enhanced configuration management with comprehensive error handling."""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dotenv import load_dotenv

from ..error_handling.exceptions import ConfigurationError
from ..error_handling.logger import logger


class Config:
    """Enhanced application configuration manager with comprehensive error handling."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.config = {}
        self.env_vars = {}
        
        try:
            # Load configuration
            self.config = self._load_config()
            
            # Load environment variables with error handling
            self._load_env_vars()
            
            # Validate configuration
            self._validate_config()
            
            logger.info(f"Configuration loaded successfully from {config_path}")
            
        except Exception as e:
            logger.error(f"Configuration initialization failed: {e}", exc_info=True)
            # Use default config as fallback
            self.config = self._get_default_config()
            logger.info("Using default configuration as fallback")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file with comprehensive error handling."""
        try:
            config_file = Path(self.config_path)
            
            if not config_file.exists():
                logger.warning(f"Config file not found: {self.config_path}")
                return self._get_default_config()
            
            # Check file size to prevent loading huge files
            file_size = config_file.stat().st_size
            if file_size > 1024 * 1024:  # 1MB limit
                logger.error(f"Config file too large: {file_size} bytes")
                raise ConfigurationError(f"Config file too large: {file_size} bytes")
            
            # Load YAML with encoding detection
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
            except UnicodeDecodeError:
                # Try with different encodings
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        with open(config_file, 'r', encoding=encoding) as f:
                            config = yaml.safe_load(f)
                        logger.warning(f"Loaded config with {encoding} encoding")
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ConfigurationError(f"Cannot decode config file: {self.config_path}")
            
            if not isinstance(config, dict):
                logger.error("Config file does not contain valid YAML dictionary")
                raise ConfigurationError("Invalid config file format")
            
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
            
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in config file: {e}")
            raise ConfigurationError(f"YAML parsing error: {e}")
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            raise ConfigurationError(f"Failed to load config: {e}")
    
    def _load_env_vars(self) -> None:
        """Load environment variables with error handling."""
        try:
            # Try to load .env file if it exists
            env_file = Path('.env')
            if env_file.exists():
                try:
                    load_dotenv()
                    logger.info("Environment variables loaded from .env file")
                except Exception as e:
                    logger.warning(f"Could not load .env file: {e}")
                    # Continue without .env file
            else:
                logger.info("No .env file found, using system environment variables")
            
            # Load critical environment variables
            self.env_vars = {
                'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
                'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
                'DEBUG': os.getenv('DEBUG', 'false').lower() == 'true',
                'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO').upper()
            }
            
            logger.debug(f"Environment variables loaded: {list(self.env_vars.keys())}")
            
        except Exception as e:
            logger.error(f"Error loading environment variables: {e}")
            # Set defaults
            self.env_vars = {
                'GEMINI_API_KEY': '',
                'OPENAI_API_KEY': '',
                'DEBUG': False,
                'LOG_LEVEL': 'INFO'
            }
    
    def _validate_config(self) -> None:
        """Validate configuration values."""
        try:
            # Validate required sections
            required_sections = ['recording', 'storage', 'llm', 'processing']
            for section in required_sections:
                if section not in self.config:
                    logger.warning(f"Missing config section: {section}")
                    self.config[section] = self._get_default_config()[section]
            
            # Validate recording settings
            recording = self.config.get('recording', {})
            if not isinstance(recording.get('fps'), (int, float)) or recording.get('fps', 0) <= 0:
                logger.warning("Invalid FPS setting, using default")
                recording['fps'] = 1
            
            if not isinstance(recording.get('audio_sample_rate'), int) or recording.get('audio_sample_rate', 0) <= 0:
                logger.warning("Invalid audio sample rate, using default")
                recording['audio_sample_rate'] = 16000
            
            # Validate storage settings
            storage = self.config.get('storage', {})
            if not isinstance(storage.get('max_storage_gb'), (int, float)) or storage.get('max_storage_gb', 0) <= 0:
                logger.warning("Invalid max storage setting, using default")
                storage['max_storage_gb'] = 5
            
            # Validate LLM settings
            llm = self.config.get('llm', {})
            if llm.get('provider') not in ['gemini', 'openai']:
                logger.warning("Invalid LLM provider, using default")
                llm['provider'] = 'gemini'
            
            logger.info("Configuration validation completed")
            
        except Exception as e:
            logger.error(f"Configuration validation error: {e}")
            # Use default config
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration with comprehensive settings."""
        return {
            'recording': {
                'max_duration_minutes': 60,
                'fps': 1,
                'audio_sample_rate': 16000,
                'audio_channels': 1,
                'chunk_duration_minutes': 1,
                'screenshot_interval_seconds': 5,
                'frame_resize_width': 1280,
                'frame_resize_height': 720,
                'quality': 85
            },
            'storage': {
                'local_path': './user_data',
                'temp_path': './user_data/temp',
                'recordings_path': './user_data/recordings',
                'processed_path': './user_data/processed',
                'logs_path': './user_data/logs',
                'cache_path': './user_data/cache',
                'auto_delete_raw': True,
                'max_storage_gb': 5,
                'cleanup_interval_hours': 24,
                'backup_retention_days': 30
            },
            'llm': {
                'provider': 'gemini',
                'model': 'gemini-2.0-flash-exp',
                'temperature': 0.3,
                'max_tokens': 2000,
                'timeout_seconds': 30,
                'max_retries': 3,
                'retry_delay_seconds': 1
            },
            'processing': {
                'max_workers': 4,
                'timeout_seconds': 300,
                'frame_resize_width': 1280,
                'frame_resize_height': 720,
                'frame_quality': 85,
                'max_frames_per_video': 1000,
                'frame_extraction_timeout': 300,
                'max_concurrent_extractions': 4,
                'audio_sample_rate': 16000,
                'audio_channels': 1,
                'max_audio_duration': 3600,
                'min_audio_duration': 0.1,
                'transcription_timeout': 300,
                'max_concurrent_transcriptions': 2
            },
            'ui': {
                'window_width': 1000,
                'window_height': 700,
                'font_size': 12,
                'font_family': 'Arial',
                'theme': 'light'
            },
            'performance': {
                'memory_limit_mb': 1024,
                'cpu_limit_percent': 80,
                'max_workers': 4,
                'processing_timeout_seconds': 300,
                'cache_size_mb': 100
            },
            'security': {
                'encryption_algorithm': 'AES-256',
                'key_length': 256,
                'blur_level': 'medium',
                'blur_radius': 5
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated path with error handling."""
        try:
            keys = key_path.split('.')
            value = self.config
            
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    return default
            
            return value if value is not None else default
            
        except Exception as e:
            logger.error(f"Error getting config value for {key_path}: {e}")
            return default
    
    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value by dot-separated path."""
        try:
            keys = key_path.split('.')
            config = self.config
            
            # Navigate to the parent of the target key
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            
            # Set the value
            config[keys[-1]] = value
            logger.debug(f"Set config value: {key_path} = {value}")
            
        except Exception as e:
            logger.error(f"Error setting config value for {key_path}: {e}")
    
    def get_api_key(self, provider: str = 'gemini') -> str:
        """Get API key from environment with validation."""
        try:
            if provider == 'gemini':
                api_key = self.env_vars.get('GEMINI_API_KEY', '')
            elif provider == 'openai':
                api_key = self.env_vars.get('OPENAI_API_KEY', '')
            else:
                logger.warning(f"Unknown API provider: {provider}")
                return ''
            
            if not api_key:
                logger.warning(f"No API key found for provider: {provider}")
                return ''
            
            # Basic validation
            if len(api_key) < 10:
                logger.warning(f"API key for {provider} appears to be invalid (too short)")
                return ''
            
            logger.debug(f"API key retrieved for provider: {provider}")
            return api_key
            
        except Exception as e:
            logger.error(f"Error getting API key for {provider}: {e}")
            return ''
    
    def has_api_key(self, provider: str = 'gemini') -> bool:
        """Check if API key is available for provider."""
        return bool(self.get_api_key(provider))
    
    def get_env_var(self, key: str, default: Any = None) -> Any:
        """Get environment variable with error handling."""
        try:
            return self.env_vars.get(key, default)
        except Exception as e:
            logger.error(f"Error getting environment variable {key}: {e}")
            return default
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.get_env_var('DEBUG', False)
    
    def get_log_level(self) -> str:
        """Get log level setting."""
        return self.get_env_var('LOG_LEVEL', 'INFO')
    
    def save_config(self, file_path: Optional[str] = None) -> bool:
        """Save current configuration to file."""
        try:
            save_path = Path(file_path) if file_path else Path(self.config_path)
            
            # Ensure directory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save with proper formatting
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def reload_config(self) -> bool:
        """Reload configuration from file."""
        try:
            self.config = self._load_config()
            self._validate_config()
            logger.info("Configuration reloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error reloading configuration: {e}")
            return False
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get complete configuration dictionary."""
        return self.config.copy()
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for logging."""
        try:
            return {
                'config_file': self.config_path,
                'sections': list(self.config.keys()),
                'has_gemini_key': self.has_api_key('gemini'),
                'has_openai_key': self.has_api_key('openai'),
                'debug_mode': self.is_debug_mode(),
                'log_level': self.get_log_level(),
                'env_vars_count': len(self.env_vars)
            }
        except Exception as e:
            logger.error(f"Error getting config summary: {e}")
            return {}


# Global config instance with error handling
try:
    config = Config()
    logger.info("Global configuration instance created successfully")
except Exception as e:
    logger.error(f"Failed to create global configuration: {e}")
    # Create minimal fallback config
    config = Config()
