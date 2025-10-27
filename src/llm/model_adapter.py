"""Model adaptation and learning over time."""
import json
from ..utils.helpers import save_json, load_json
from ..error_handling.logger import logger


class ModelAdapter:
    """Adapts model behavior based on user patterns over time."""
    
    def __init__(self, storage):
        self.storage = storage
        self.user_patterns_file = storage.get_processed_file_path('user_patterns.json')
        self.patterns = self._load_patterns()
    
    def _load_patterns(self):
        """Load previously learned patterns."""
        data = load_json(self.user_patterns_file)
        return data if data else {
            'workflows': [],
            'frequent_apps': [],
            'time_patterns': {},
            'learned_at': []
        }
    
    def _save_patterns(self):
        """Save learned patterns."""
        save_json(self.patterns, self.user_patterns_file)
    
    def update_patterns(self, new_workflows):
        """Update patterns with new workflow data."""
        try:
            from datetime import datetime
            
            # Add new workflows
            for workflow in new_workflows:
                # Check if similar workflow exists
                similar = False
                for existing in self.patterns['workflows']:
                    if self._is_similar_workflow(workflow, existing):
                        # Increment count
                        existing['count'] = existing.get('count', 1) + 1
                        existing['last_seen'] = datetime.now().isoformat()
                        similar = True
                        break
                
                if not similar:
                    workflow['count'] = 1
                    workflow['first_seen'] = datetime.now().isoformat()
                    workflow['last_seen'] = datetime.now().isoformat()
                    self.patterns['workflows'].append(workflow)
            
            # Update learned timestamp
            self.patterns['learned_at'].append(datetime.now().isoformat())
            
            # Save patterns
            self._save_patterns()
            logger.info("Updated user patterns")
        except Exception as e:
            logger.error(f"Error updating patterns: {e}")
    
    def _is_similar_workflow(self, workflow1, workflow2):
        """Check if two workflows are similar."""
        desc1 = workflow1.get('description', '').lower()
        desc2 = workflow2.get('description', '').lower()
        
        # Simple similarity check based on keywords
        keywords1 = set(desc1.split())
        keywords2 = set(desc2.split())
        
        common = keywords1.intersection(keywords2)
        return len(common) >= 2
    
    def get_top_workflows(self, limit=5):
        """Get most frequent workflows."""
        sorted_workflows = sorted(
            self.patterns['workflows'],
            key=lambda x: x.get('count', 0),
            reverse=True
        )
        return sorted_workflows[:limit]
    
    def get_insights(self):
        """Get insights from learned patterns."""
        insights = {
            'total_workflows_learned': len(self.patterns['workflows']),
            'most_common_workflow': None,
            'learning_sessions': len(self.patterns['learned_at'])
        }
        
        if self.patterns['workflows']:
            most_common = max(
                self.patterns['workflows'],
                key=lambda x: x.get('count', 0)
            )
            insights['most_common_workflow'] = most_common.get('description')
        
        return insights
