"""Simplified configuration management."""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class SimpleConfig:
    """Simplified configuration manager."""
    
    def __init__(self):
        self.config = self._load_default_config()
        self._load_env_vars()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        return {
            'recording': {
                'fps': 1,
                'max_duration_minutes': 0,  # 0 = indefinite recording
                'audio_sample_rate': 16000,
                'indefinite_recording': True
            },
            'storage': {
                'local_path': './user_data',
                'temp_path': './user_data/temp',
                'recordings_path': './user_data/recordings',
                'processed_path': './user_data/processed',
                'max_storage_gb': 5
            },
            'llm': {
                'provider': 'openai',
                'model': 'gpt-3.5-turbo',
                'temperature': 0.3,
                'max_tokens': 2000,
                'timeout_seconds': 30
            },
            'processing': {
                'max_workers': 4,
                'timeout_seconds': 300
            }
        }
    
    def _load_env_vars(self):
        """Load environment variables."""
        # Load from .env file if it exists
        env_file = Path('.env')
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
            except Exception as e:
                print(f"Warning: Could not load .env file: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated path."""
        try:
            keys = key_path.split('.')
            value = self.config
            
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    return default
            
            return value if value is not None else default
        except Exception:
            return default
    
    def get_api_key(self, provider: str = 'openai') -> str:
        """Get API key from environment."""
        if provider == 'openai':
            return os.getenv('OPENAI_API_KEY', '')
        elif provider == 'gemini':
            return os.getenv('GEMINI_API_KEY', '')
        return ''
    
    def has_api_key(self, provider: str = 'openai') -> bool:
        """Check if API key is available."""
        return bool(self.get_api_key(provider))


# Global config instance
config = SimpleConfig()
