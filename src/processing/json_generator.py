"""JSON data structure generation."""
import json
from datetime import datetime
from ..utils.helpers import save_json
from ..error_handling.logger import logger


class JSONGenerator:
    """Generates structured JSON data from processed information."""
    
    def __init__(self, storage):
        self.storage = storage
    
    def generate_session_summary(self, session_data, frames_data, audio_data, workflows):
        """Generate comprehensive session summary JSON."""
        try:
            summary = {
                'session_id': session_data.get('id', 'unknown'),
                'timestamp': datetime.now().isoformat(),
                'session_info': {
                    'start_time': session_data.get('start_time'),
                    'end_time': session_data.get('end_time'),
                    'duration_seconds': session_data.get('duration', 0)
                },
                'capture_data': {
                    'total_frames': len(frames_data),
                    'frames': frames_data[:10],  # First 10 frames for summary
                    'audio_transcription': audio_data.get('transcription', '')
                },
                'detected_workflows': workflows,
                'metadata': {
                    'processed_at': datetime.now().isoformat(),
                    'version': '1.0.0'
                }
            }
            
            # Save to file
            filename = f"session_{session_data.get('id', 'unknown')}_summary.json"
            filepath = self.storage.get_processed_file_path(filename)
            save_json(summary, filepath)
            
            logger.info(f"Generated session summary: {filepath}")
            return summary
        except Exception as e:
            logger.error(f"Error generating session summary: {e}")
            return None
    
    def generate_workflow_json(self, workflows):
        """Generate workflow-specific JSON."""
        try:
            workflow_data = {
                'timestamp': datetime.now().isoformat(),
                'total_workflows': len(workflows),
                'workflows': workflows
            }
            
            filename = f"workflows_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.storage.get_processed_file_path(filename)
            save_json(workflow_data, filepath)
            
            logger.info(f"Generated workflow JSON: {filepath}")
            return workflow_data
        except Exception as e:
            logger.error(f"Error generating workflow JSON: {e}")
            return None
