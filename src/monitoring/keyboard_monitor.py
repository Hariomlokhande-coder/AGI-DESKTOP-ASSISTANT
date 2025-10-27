"""
Real-time keyboard monitoring system for tracking key actions.
"""

import time
import logging
from typing import Dict, List, Optional, Callable, Set
from datetime import datetime
import threading
import queue
from collections import deque

try:
    import pynput
    from pynput import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

try:
    from error_handling.simple_logger import logger
except ImportError:
    from src.error_handling.simple_logger import logger


class KeyboardMonitor:
    """Monitor keyboard input and detect key actions in real-time."""
    
    def __init__(self, callback: Optional[Callable] = None):
        self.callback = callback
        self.running = False
        self.key_events = deque(maxlen=1000)  # Keep last 1000 key events
        self.current_keys = set()  # Currently pressed keys
        self.typing_buffer = ""
        self.last_typing_time = 0
        self.typing_timeout = 2.0  # Seconds of inactivity before processing typing buffer
        
        # Key action patterns
        self.action_patterns = {
            'save': ['ctrl+s', 'ctrl+shift+s'],
            'open': ['ctrl+o'],
            'new': ['ctrl+n'],
            'close': ['ctrl+w', 'alt+f4'],
            'copy': ['ctrl+c'],
            'paste': ['ctrl+v'],
            'cut': ['ctrl+x'],
            'undo': ['ctrl+z'],
            'redo': ['ctrl+y', 'ctrl+shift+z'],
            'find': ['ctrl+f'],
            'replace': ['ctrl+h'],
            'select_all': ['ctrl+a'],
            'print': ['ctrl+p'],
            'refresh': ['f5', 'ctrl+r'],
            'search': ['ctrl+f', 'ctrl+shift+f'],
            'zoom_in': ['ctrl+plus', 'ctrl+='],
            'zoom_out': ['ctrl+minus', 'ctrl+-'],
            'tab_switch': ['ctrl+tab', 'alt+tab'],
            'close_tab': ['ctrl+w'],
            'new_tab': ['ctrl+t'],
            'reopen_tab': ['ctrl+shift+t']
        }
        
        # Special key mappings
        self.special_keys = {
            'Key.space': ' ',
            'Key.enter': '\n',
            'Key.tab': '\t',
            'Key.backspace': '[BACKSPACE]',
            'Key.delete': '[DELETE]',
            'Key.esc': '[ESC]',
            'Key.shift': '[SHIFT]',
            'Key.ctrl': '[CTRL]',
            'Key.alt': '[ALT]',
            'Key.cmd': '[CMD]',
            'Key.up': '[UP]',
            'Key.down': '[DOWN]',
            'Key.left': '[LEFT]',
            'Key.right': '[RIGHT]',
            'Key.home': '[HOME]',
            'Key.end': '[END]',
            'Key.page_up': '[PAGE_UP]',
            'Key.page_down': '[PAGE_DOWN]',
            'Key.f1': '[F1]',
            'Key.f2': '[F2]',
            'Key.f3': '[F3]',
            'Key.f4': '[F4]',
            'Key.f5': '[F5]',
            'Key.f6': '[F6]',
            'Key.f7': '[F7]',
            'Key.f8': '[F8]',
            'Key.f9': '[F9]',
            'Key.f10': '[F10]',
            'Key.f11': '[F11]',
            'Key.f12': '[F12]'
        }
        
        # Modifier keys
        self.modifier_keys = {'Key.ctrl', 'Key.alt', 'Key.shift', 'Key.cmd'}
        
        logger.info("KeyboardMonitor initialized")
    
    def start_monitoring(self):
        """Start keyboard monitoring."""
        if not KEYBOARD_AVAILABLE:
            logger.error("pynput not available. Keyboard monitoring disabled.")
            return False
        
        if self.running:
            logger.warning("Keyboard monitoring is already running")
            return False
        
        try:
            self.running = True
            self.listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.listener.start()
            
            # Start typing buffer processor
            self.typing_thread = threading.Thread(target=self._process_typing_buffer, daemon=True)
            self.typing_thread.start()
            
            logger.info("Keyboard monitoring started")
            return True
        except Exception as e:
            logger.error(f"Failed to start keyboard monitoring: {e}")
            self.running = False
            return False
    
    def stop_monitoring(self):
        """Stop keyboard monitoring."""
        if not self.running:
            return
        
        self.running = False
        if hasattr(self, 'listener'):
            self.listener.stop()
        logger.info("Keyboard monitoring stopped")
    
    def _on_key_press(self, key):
        """Handle key press events."""
        try:
            current_time = time.time()
            key_str = self._key_to_string(key)
            
            # Add to current keys
            self.current_keys.add(key_str)
            
            # Create key event
            key_event = {
                'action': 'press',
                'key': key_str,
                'timestamp': datetime.now(),
                'time': current_time,
                'modifiers': self._get_current_modifiers()
            }
            
            # Add to events
            self.key_events.append(key_event)
            
            # Handle typing buffer
            if self._is_typing_key(key_str):
                self.typing_buffer += self._get_typing_char(key_str)
                self.last_typing_time = current_time
            
            # Check for action patterns
            self._check_action_patterns()
            
            # Call callback
            if self.callback:
                self.callback(key_event)
                
        except Exception as e:
            logger.error(f"Error in key press handler: {e}")
    
    def _on_key_release(self, key):
        """Handle key release events."""
        try:
            current_time = time.time()
            key_str = self._key_to_string(key)
            
            # Remove from current keys
            self.current_keys.discard(key_str)
            
            # Create key event
            key_event = {
                'action': 'release',
                'key': key_str,
                'timestamp': datetime.now(),
                'time': current_time,
                'modifiers': self._get_current_modifiers()
            }
            
            # Add to events
            self.key_events.append(key_event)
            
        except Exception as e:
            logger.error(f"Error in key release handler: {e}")
    
    def _key_to_string(self, key) -> str:
        """Convert pynput key to string representation."""
        try:
            if hasattr(key, 'char') and key.char is not None:
                return key.char
            else:
                return str(key)
        except:
            return str(key)
    
    def _get_current_modifiers(self) -> Set[str]:
        """Get currently pressed modifier keys."""
        modifiers = set()
        for key in self.current_keys:
            if key in self.modifier_keys:
                modifiers.add(key)
        return modifiers
    
    def _is_typing_key(self, key_str: str) -> bool:
        """Check if key represents typing input."""
        # Exclude modifier keys and special keys
        if key_str in self.modifier_keys:
            return False
        if key_str.startswith('Key.') and key_str not in self.special_keys:
            return False
        return True
    
    def _get_typing_char(self, key_str: str) -> str:
        """Get the character representation for typing."""
        if key_str in self.special_keys:
            return self.special_keys[key_str]
        return key_str
    
    def _check_action_patterns(self):
        """Check if current key combination matches any action patterns."""
        try:
            current_combo = self._get_current_key_combo()
            
            for action, patterns in self.action_patterns.items():
                if current_combo in patterns:
                    self._handle_action_detected(action, current_combo)
                    
        except Exception as e:
            logger.error(f"Error checking action patterns: {e}")
    
    def _get_current_key_combo(self) -> str:
        """Get current key combination string."""
        modifiers = []
        regular_keys = []
        
        for key in self.current_keys:
            if key in self.modifier_keys:
                modifiers.append(key.replace('Key.', '').lower())
            else:
                regular_keys.append(key)
        
        if not regular_keys:
            return ""
        
        # Sort modifiers for consistency
        modifiers.sort()
        combo = '+'.join(modifiers + regular_keys)
        return combo
    
    def _handle_action_detected(self, action: str, combo: str):
        """Handle when an action is detected."""
        try:
            action_event = {
                'type': 'action',
                'action': action,
                'combo': combo,
                'timestamp': datetime.now(),
                'time': time.time()
            }
            
            # Log the action with detailed label
            timestamp = action_event['timestamp'].strftime("%H:%M:%S")
            # Map action to detailed label
            action_labels = {
                'save': f'[FILE ACTION] Saved file',
                'open': f'[FILE ACTION] Opened file',
                'close': f'[FILE ACTION] Closed file',
                'copy': f'[EDIT ACTION] Copied',
                'paste': f'[EDIT ACTION] Pasted',
                'cut': f'[EDIT ACTION] Cut',
                'undo': f'[EDIT ACTION] Undone',
                'redo': f'[EDIT ACTION] Redone',
            }
            action_label = action_labels.get(action, f'[ACTION] {action.title()}')
            logger.info(f"{action_label} - {combo} ({timestamp})")
            
            # Add to events
            self.key_events.append(action_event)
            
            # Call callback
            if self.callback:
                self.callback(action_event)
                
        except Exception as e:
            logger.error(f"Error handling action detected: {e}")
    
    def _process_typing_buffer(self):
        """Process the typing buffer periodically."""
        while self.running:
            try:
                current_time = time.time()
                
                # Check if typing buffer has content and timeout has passed
                if (self.typing_buffer and 
                    current_time - self.last_typing_time > self.typing_timeout):
                    
                    # Process the typing buffer
                    self._process_typing_content(self.typing_buffer)
                    self.typing_buffer = ""
                
                time.sleep(0.1)  # Check every 100ms
                
            except Exception as e:
                logger.error(f"Error in typing buffer processor: {e}")
                time.sleep(1)
    
    def _process_typing_content(self, content: str):
        """Process typed content."""
        try:
            if not content.strip():
                return
            
            # Clean up the content
            cleaned_content = content.strip()
            
            # Detect typing patterns
            typing_event = {
                'type': 'typing',
                'content': cleaned_content,
                'length': len(cleaned_content),
                'timestamp': datetime.now(),
                'time': time.time()
            }
            
            # Log typing with preview
            timestamp = typing_event['timestamp'].strftime("%H:%M:%S")
            preview = cleaned_content[:50] + "..." if len(cleaned_content) > 50 else cleaned_content
            logger.info(f"[TYPING] Typed {len(cleaned_content)} chars: {preview} ({timestamp})")
            
            # Add to events
            self.key_events.append(typing_event)
            
            # Call callback
            if self.callback:
                self.callback(typing_event)
                
        except Exception as e:
            logger.error(f"Error processing typing content: {e}")
    
    def get_recent_events(self, limit: int = 50) -> List[Dict]:
        """Get recent keyboard events."""
        return list(self.key_events)[-limit:] if self.key_events else []
    
    def get_typing_stats(self) -> Dict:
        """Get typing statistics."""
        typing_events = [e for e in self.key_events if e.get('type') == 'typing']
        
        if not typing_events:
            return {'total_chars': 0, 'total_events': 0, 'avg_length': 0}
        
        total_chars = sum(e.get('length', 0) for e in typing_events)
        total_events = len(typing_events)
        avg_length = total_chars / total_events if total_events > 0 else 0
        
        return {
            'total_chars': total_chars,
            'total_events': total_events,
            'avg_length': avg_length
        }
    
    def get_action_stats(self) -> Dict[str, int]:
        """Get action statistics."""
        action_events = [e for e in self.key_events if e.get('type') == 'action']
        
        stats = {}
        for event in action_events:
            action = event.get('action', 'unknown')
            stats[action] = stats.get(action, 0) + 1
        
        return stats
    
    def clear_events(self):
        """Clear all stored events."""
        self.key_events.clear()
        self.typing_buffer = ""
        logger.info("Keyboard events cleared")


class KeyboardActionClassifier:
    """Classify keyboard actions into meaningful categories."""
    
    def __init__(self):
        self.action_categories = {
            'file_operations': ['save', 'open', 'new', 'close', 'print'],
            'edit_operations': ['copy', 'paste', 'cut', 'undo', 'redo', 'select_all'],
            'navigation': ['find', 'replace', 'tab_switch', 'close_tab', 'new_tab'],
            'view_operations': ['zoom_in', 'zoom_out', 'refresh'],
            'typing': ['typing']
        }
        
        logger.info("KeyboardActionClassifier initialized")
    
    def classify_action(self, event: Dict) -> str:
        """Classify a keyboard event into a category."""
        if event.get('type') == 'typing':
            return 'typing'
        
        action = event.get('action', '')
        
        for category, actions in self.action_categories.items():
            if action in actions:
                return category
        
        return 'other'
    
    def get_action_summary(self, events: List[Dict]) -> Dict[str, int]:
        """Get a summary of actions by category."""
        summary = {}
        
        for event in events:
            category = self.classify_action(event)
            summary[category] = summary.get(category, 0) + 1
        
        return summary
