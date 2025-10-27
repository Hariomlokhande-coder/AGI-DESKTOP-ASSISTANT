"""
Action classifier for categorizing and analyzing user actions.
"""

import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
import re

try:
    from error_handling.simple_logger import logger
except ImportError:
    from src.error_handling.simple_logger import logger


class ActionClassifier:
    """Classify and categorize user actions from various sources."""
    
    def __init__(self):
        self.action_history = deque(maxlen=1000)  # Keep last 1000 actions
        self.action_patterns = {}
        self.workflow_sessions = []
        self.current_session = None
        
        # Action categories and their patterns
        self.action_categories = {
            'app_switching': {
                'keywords': ['app opened', 'window switch', 'application'],
                'patterns': [r'\[App Opened\]', r'\[Window Switch\]'],
                'weight': 1.0
            },
            'typing': {
                'keywords': ['typed', 'typing', 'text input', 'data entry'],
                'patterns': [r'\[Typed\]', r'\[Text Input\]'],
                'weight': 0.8
            },
            'file_operations': {
                'keywords': ['save', 'open', 'close', 'file', 'document'],
                'patterns': [r'\[Saved File\]', r'\[Opened File\]', r'\[Closed File\]'],
                'weight': 1.2
            },
            'navigation': {
                'keywords': ['browse', 'url', 'search', 'navigate'],
                'patterns': [r'\[Browsed URL\]', r'\[Search\]', r'\[Navigation\]'],
                'weight': 0.9
            },
            'editing': {
                'keywords': ['edit', 'modify', 'change', 'format', 'copy', 'paste'],
                'patterns': [r'\[Edit\]', r'\[Format\]', r'\[Copy\]', r'\[Paste\]'],
                'weight': 0.7
            },
            'calculation': {
                'keywords': ['calculate', 'formula', 'sum', 'average', 'excel'],
                'patterns': [r'\[Calculation\]', r'\[Formula\]', r'\[Excel\]'],
                'weight': 1.1
            },
            'communication': {
                'keywords': ['email', 'message', 'chat', 'teams', 'outlook'],
                'patterns': [r'\[Email\]', r'\[Message\]', r'\[Chat\]'],
                'weight': 1.0
            },
            'system': {
                'keywords': ['system', 'settings', 'config', 'admin'],
                'patterns': [r'\[System\]', r'\[Settings\]'],
                'weight': 0.5
            }
        }
        
        # Application-specific action mappings
        self.app_action_mappings = {
            'excel': {
                'data_entry': 'typing',
                'formula': 'calculation',
                'chart': 'editing',
                'filter': 'editing',
                'pivot': 'calculation'
            },
            'word': {
                'typing': 'typing',
                'formatting': 'editing',
                'review': 'editing',
                'insert': 'editing'
            },
            'browser': {
                'browsing': 'navigation',
                'searching': 'navigation',
                'shopping': 'navigation',
                'social': 'communication'
            },
            'outlook': {
                'email': 'communication',
                'calendar': 'communication',
                'contacts': 'communication'
            },
            'teams': {
                'meeting': 'communication',
                'chat': 'communication',
                'call': 'communication'
            }
        }
        
        logger.info("ActionClassifier initialized")
    
    def classify_action(self, action_data: Dict) -> Dict[str, Any]:
        """Classify an action and return detailed analysis."""
        try:
            # Extract basic information
            action_type = action_data.get('type', 'unknown')
            timestamp = action_data.get('timestamp', datetime.now())
            content = action_data.get('content', '')
            app_name = action_data.get('app_name', '')
            
            # Determine primary category
            primary_category = self._determine_primary_category(action_data)
            
            # Determine subcategory
            subcategory = self._determine_subcategory(action_data, primary_category)
            
            # Calculate confidence
            confidence = self._calculate_confidence(action_data, primary_category)
            
            # Detect workflow context
            workflow_context = self._detect_workflow_context(action_data)
            
            # Create classified action
            classified_action = {
                'original_data': action_data,
                'primary_category': primary_category,
                'subcategory': subcategory,
                'confidence': confidence,
                'workflow_context': workflow_context,
                'timestamp': timestamp,
                'app_name': app_name,
                'content_preview': self._create_content_preview(content),
                'action_id': self._generate_action_id(action_data)
            }
            
            # Add to history
            self.action_history.append(classified_action)
            
            # Update workflow session
            self._update_workflow_session(classified_action)
            
            return classified_action
            
        except Exception as e:
            logger.error(f"Error classifying action: {e}")
            return self._create_error_action(action_data, str(e))
    
    def _determine_primary_category(self, action_data: Dict) -> str:
        """Determine the primary category for an action."""
        content = str(action_data.get('content', '')).lower()
        action_type = action_data.get('type', '').lower()
        app_name = action_data.get('app_name', '').lower()
        
        # Check for explicit action patterns
        for category, config in self.action_categories.items():
            # Check keywords
            for keyword in config['keywords']:
                if keyword in content or keyword in action_type:
                    return category
            
            # Check regex patterns
            for pattern in config['patterns']:
                if re.search(pattern, content, re.IGNORECASE):
                    return category
        
        # Check application-specific mappings
        if app_name in self.app_action_mappings:
            app_actions = self.app_action_mappings[app_name]
            for action_key, category in app_actions.items():
                if action_key in content or action_key in action_type:
                    return category
        
        # Default categorization based on action type
        if action_type == 'typing':
            return 'typing'
        elif action_type == 'action':
            return 'editing'
        elif 'app' in action_type or 'window' in action_type:
            return 'app_switching'
        else:
            return 'unknown'
    
    def _determine_subcategory(self, action_data: Dict, primary_category: str) -> str:
        """Determine the subcategory for an action."""
        content = str(action_data.get('content', '')).lower()
        action_type = action_data.get('type', '').lower()
        
        # Define subcategories for each primary category
        subcategory_mappings = {
            'app_switching': {
                'excel': 'spreadsheet_app',
                'word': 'document_app',
                'chrome': 'browser_app',
                'firefox': 'browser_app',
                'edge': 'browser_app',
                'notepad': 'text_app',
                'outlook': 'email_app',
                'teams': 'communication_app'
            },
            'typing': {
                'data': 'data_entry',
                'formula': 'formula_input',
                'text': 'text_editing',
                'search': 'search_input',
                'url': 'url_input'
            },
            'file_operations': {
                'save': 'file_save',
                'open': 'file_open',
                'close': 'file_close',
                'new': 'file_new'
            },
            'navigation': {
                'browse': 'web_browsing',
                'search': 'web_search',
                'url': 'url_navigation'
            },
            'editing': {
                'copy': 'copy_operation',
                'paste': 'paste_operation',
                'cut': 'cut_operation',
                'format': 'format_operation'
            },
            'calculation': {
                'formula': 'formula_calculation',
                'sum': 'sum_calculation',
                'average': 'average_calculation',
                'excel': 'spreadsheet_calculation'
            }
        }
        
        if primary_category in subcategory_mappings:
            mappings = subcategory_mappings[primary_category]
            for keyword, subcategory in mappings.items():
                if keyword in content or keyword in action_type:
                    return subcategory
        
        return 'general'
    
    def _calculate_confidence(self, action_data: Dict, primary_category: str) -> float:
        """Calculate confidence score for the classification."""
        confidence = 0.5  # Base confidence
        
        content = str(action_data.get('content', '')).lower()
        action_type = action_data.get('type', '').lower()
        
        # Check category-specific patterns
        if primary_category in self.action_categories:
            config = self.action_categories[primary_category]
            
            # Keyword matches
            keyword_matches = sum(1 for keyword in config['keywords'] 
                                if keyword in content or keyword in action_type)
            confidence += min(keyword_matches * 0.2, 0.4)
            
            # Pattern matches
            pattern_matches = sum(1 for pattern in config['patterns'] 
                                if re.search(pattern, content, re.IGNORECASE))
            confidence += min(pattern_matches * 0.3, 0.3)
            
            # Apply category weight
            confidence *= config['weight']
        
        # Content length factor
        if len(content) > 10:
            confidence += 0.1
        
        # App name factor
        if action_data.get('app_name'):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _detect_workflow_context(self, action_data: Dict) -> Dict[str, Any]:
        """Detect workflow context from recent actions."""
        context = {
            'session_type': 'unknown',
            'workflow_stage': 'unknown',
            'related_actions': [],
            'time_since_last_action': 0
        }
        
        if not self.action_history:
            return context
        
        # Get recent actions (last 10)
        recent_actions = list(self.action_history)[-10:]
        
        # Calculate time since last action
        if len(recent_actions) > 1:
            last_action = recent_actions[-2]
            time_diff = (action_data.get('timestamp', datetime.now()) - 
                        last_action['timestamp']).total_seconds()
            context['time_since_last_action'] = time_diff
        
        # Detect session type based on recent actions
        recent_categories = [action['primary_category'] for action in recent_actions[-5:]]
        category_counts = defaultdict(int)
        for category in recent_categories:
            category_counts[category] += 1
        
        # Determine session type
        if category_counts['typing'] > 2:
            context['session_type'] = 'content_creation'
        elif category_counts['calculation'] > 1:
            context['session_type'] = 'data_analysis'
        elif category_counts['navigation'] > 2:
            context['session_type'] = 'research'
        elif category_counts['communication'] > 1:
            context['session_type'] = 'communication'
        else:
            context['session_type'] = 'general_work'
        
        # Find related actions
        current_app = action_data.get('app_name', '')
        if current_app:
            related_actions = [action for action in recent_actions 
                             if action.get('app_name') == current_app]
            context['related_actions'] = related_actions[-3:]  # Last 3 related actions
        
        return context
    
    def _create_content_preview(self, content: str) -> str:
        """Create a preview of the content."""
        if not content:
            return ""
        
        # Clean up content
        cleaned = re.sub(r'[^\w\s]', '', str(content))
        
        # Truncate if too long
        if len(cleaned) > 50:
            return cleaned[:47] + "..."
        
        return cleaned
    
    def _generate_action_id(self, action_data: Dict) -> str:
        """Generate a unique ID for the action."""
        timestamp = action_data.get('timestamp', datetime.now())
        content_hash = hash(str(action_data.get('content', ''))) % 10000
        return f"{timestamp.strftime('%H%M%S')}_{abs(content_hash)}"
    
    def _update_workflow_session(self, classified_action: Dict):
        """Update the current workflow session."""
        current_time = classified_action['timestamp']
        
        # Start new session if needed
        if not self.current_session:
            self.current_session = {
                'start_time': current_time,
                'actions': [],
                'session_type': 'unknown',
                'apps_used': set()
            }
        
        # Check if session should continue (within 30 minutes of last action)
        if self.action_history:
            last_action = self.action_history[-1]
            time_diff = (current_time - last_action['timestamp']).total_seconds()
            
            if time_diff > 1800:  # 30 minutes
                # End current session and start new one
                self._end_current_session()
                self.current_session = {
                    'start_time': current_time,
                    'actions': [],
                    'session_type': 'unknown',
                    'apps_used': set()
                }
        
        # Add action to current session
        self.current_session['actions'].append(classified_action)
        if classified_action.get('app_name'):
            self.current_session['apps_used'].add(classified_action['app_name'])
        
        # Update session type
        self.current_session['session_type'] = classified_action['workflow_context']['session_type']
    
    def _end_current_session(self):
        """End the current workflow session."""
        if self.current_session:
            self.current_session['end_time'] = datetime.now()
            self.current_session['duration'] = (
                self.current_session['end_time'] - self.current_session['start_time']
            ).total_seconds()
            self.current_session['apps_used'] = list(self.current_session['apps_used'])
            
            self.workflow_sessions.append(self.current_session)
            self.current_session = None
    
    def get_action_summary(self, time_range_minutes: int = 60) -> Dict[str, Any]:
        """Get a summary of actions within a time range."""
        cutoff_time = datetime.now() - timedelta(minutes=time_range_minutes)
        
        recent_actions = [
            action for action in self.action_history
            if action['timestamp'] >= cutoff_time
        ]
        
        if not recent_actions:
            return {'total_actions': 0, 'categories': {}, 'apps': {}}
        
        # Count by category
        category_counts = defaultdict(int)
        app_counts = defaultdict(int)
        
        for action in recent_actions:
            category_counts[action['primary_category']] += 1
            if action.get('app_name'):
                app_counts[action['app_name']] += 1
        
        return {
            'total_actions': len(recent_actions),
            'time_range_minutes': time_range_minutes,
            'categories': dict(category_counts),
            'apps': dict(app_counts),
            'most_active_category': max(category_counts, key=category_counts.get) if category_counts else None,
            'most_used_app': max(app_counts, key=app_counts.get) if app_counts else None
        }
    
    def get_workflow_sessions(self, limit: int = 10) -> List[Dict]:
        """Get recent workflow sessions."""
        return self.workflow_sessions[-limit:] if self.workflow_sessions else []
    
    def get_current_session(self) -> Optional[Dict]:
        """Get the current workflow session."""
        return self.current_session
    
    def end_current_session(self):
        """Manually end the current session."""
        self._end_current_session()
    
    def clear_history(self):
        """Clear all action history."""
        self.action_history.clear()
        self.workflow_sessions.clear()
        self.current_session = None
        logger.info("Action history cleared")
