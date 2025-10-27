"""
OCR-based screenshot analyzer for detecting text and UI elements.
"""

import cv2
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image
import re
import os

try:
    from error_handling.simple_logger import logger
except ImportError:
    from src.error_handling.simple_logger import logger

# Try to import pytesseract, handle if not available
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("pytesseract not available. OCR features will be limited.")


class OCRAnalyzer:
    """OCR analyzer for extracting text and UI elements from screenshots."""
    
    def __init__(self):
        self.tesseract_config = '--oem 3 --psm 6'
        self.ui_elements = {
            'excel': ['Microsoft Excel', 'Excel', 'Workbook', 'Worksheet', 'Formula Bar', 'Cell', 'Row', 'Column'],
            'word': ['Microsoft Word', 'Word', 'Document', 'Page Layout', 'Insert', 'Review'],
            'browser': ['Chrome', 'Firefox', 'Edge', 'Safari', 'Address Bar', 'Tab', 'Bookmark'],
            'file_explorer': ['File Explorer', 'This PC', 'Documents', 'Downloads', 'Folder'],
            'notepad': ['Notepad', 'Text Document', 'Untitled'],
            'calculator': ['Calculator', 'Standard', 'Scientific', 'Programmer'],
            'paint': ['Paint', 'Paint 3D', 'Canvas', 'Brush', 'Color'],
            'vscode': ['Visual Studio Code', 'VS Code', 'Code', 'Terminal', 'Explorer'],
            'outlook': ['Outlook', 'Mail', 'Calendar', 'Contacts'],
            'teams': ['Microsoft Teams', 'Teams', 'Meeting', 'Chat']
        }
        
        # Common UI patterns
        self.ui_patterns = {
            'buttons': ['OK', 'Cancel', 'Save', 'Open', 'Close', 'Minimize', 'Maximize'],
            'menus': ['File', 'Edit', 'View', 'Insert', 'Format', 'Tools', 'Help'],
            'tabs': ['Home', 'Insert', 'Page Layout', 'Formulas', 'Data', 'Review', 'View'],
            'toolbars': ['Cut', 'Copy', 'Paste', 'Undo', 'Redo', 'Bold', 'Italic', 'Underline']
        }
        
        logger.info("OCRAnalyzer initialized")
    
    def analyze_screenshot(self, image_path: str) -> Dict[str, Any]:
        """Analyze a screenshot and extract text, UI elements, and context."""
        try:
            if not os.path.exists(image_path):
                logger.warning(f"Screenshot not found: {image_path}")
                return self._empty_analysis()
            
            # Load and preprocess image
            image = cv2.imread(image_path)
            if image is None:
                logger.warning(f"Could not load image: {image_path}")
                return self._empty_analysis()
            
            # Extract text using OCR
            text_data = self._extract_text(image)
            
            # Detect UI elements
            ui_elements = self._detect_ui_elements(text_data)
            
            # Detect application context
            app_context = self._detect_application_context(text_data, ui_elements)
            
            # Detect specific tasks
            tasks = self._detect_tasks(text_data, ui_elements, app_context)
            
            analysis = {
                'raw_text': text_data['raw_text'],
                'ui_elements': ui_elements,
                'application': app_context,
                'detected_tasks': tasks,
                'confidence': self._calculate_confidence(text_data, ui_elements),
                'timestamp': os.path.getmtime(image_path)
            }
            
            logger.info(f"OCR analysis completed for {image_path}")
            return analysis
            
        except Exception as e:
            logger.error(f"OCR analysis failed for {image_path}: {e}")
            return self._empty_analysis()
    
    def _extract_text(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract text from image using OCR."""
        try:
            if not TESSERACT_AVAILABLE:
                # Fallback: basic image analysis without OCR
                return self._fallback_text_extraction(image)
            
            # Convert to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
            # Extract text with different configurations
            raw_text = pytesseract.image_to_string(pil_image, config=self.tesseract_config)
            
            # Extract text with bounding boxes
            data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
            
            # Filter out low-confidence text
            confident_text = []
            for i, conf in enumerate(data['conf']):
                if int(conf) > 30:  # Confidence threshold
                    text = data['text'][i].strip()
                    if text:
                        confident_text.append({
                            'text': text,
                            'confidence': int(conf),
                            'bbox': (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                        })
            
            return {
                'raw_text': raw_text,
                'confident_text': confident_text,
                'word_count': len(confident_text)
            }
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return self._fallback_text_extraction(image)
    
    def _fallback_text_extraction(self, image: np.ndarray) -> Dict[str, Any]:
        """Fallback text extraction when OCR is not available."""
        try:
            # Basic image analysis for UI elements
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect edges and contours
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Basic UI element detection
            ui_elements = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # Filter small contours
                    x, y, w, h = cv2.boundingRect(contour)
                    ui_elements.append({
                        'text': f'UI_Element_{len(ui_elements)}',
                        'confidence': 50,
                        'bbox': (x, y, w, h)
                    })
            
            return {
                'raw_text': 'OCR not available - using basic analysis',
                'confident_text': ui_elements,
                'word_count': len(ui_elements)
            }
            
        except Exception as e:
            logger.error(f"Fallback text extraction failed: {e}")
            return {'raw_text': '', 'confident_text': [], 'word_count': 0}
    
    def _detect_ui_elements(self, text_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Detect UI elements from extracted text."""
        ui_elements = {
            'applications': [],
            'buttons': [],
            'menus': [],
            'tabs': [],
            'toolbars': [],
            'other': []
        }
        
        raw_text = text_data['raw_text'].lower()
        
        # Detect applications
        for app, keywords in self.ui_elements.items():
            for keyword in keywords:
                if keyword.lower() in raw_text:
                    ui_elements['applications'].append(app)
                    break
        
        # Detect UI patterns
        for pattern_type, patterns in self.ui_patterns.items():
            for pattern in patterns:
                if pattern.lower() in raw_text:
                    ui_elements[pattern_type].append(pattern)
        
        return ui_elements
    
    def _detect_application_context(self, text_data: Dict[str, Any], ui_elements: Dict[str, List[str]]) -> Dict[str, Any]:
        """Detect the primary application being used."""
        applications = ui_elements['applications']
        
        if not applications:
            return {'name': 'unknown', 'confidence': 0, 'context': 'general'}
        
        # Count occurrences
        app_counts = {}
        for app in applications:
            app_counts[app] = app_counts.get(app, 0) + 1
        
        # Get most frequent application
        primary_app = max(app_counts, key=app_counts.get)
        
        # Determine context based on application
        context_info = self._get_application_context(primary_app, text_data)
        
        return {
            'name': primary_app,
            'confidence': min(app_counts[primary_app] * 20, 100),
            'context': context_info,
            'all_apps': list(set(applications))
        }
    
    def _get_application_context(self, app: str, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific context for the detected application."""
        raw_text = text_data['raw_text'].lower()
        
        if app == 'excel':
            return self._analyze_excel_context(raw_text)
        elif app == 'word':
            return self._analyze_word_context(raw_text)
        elif app == 'browser':
            return self._analyze_browser_context(raw_text)
        elif app == 'file_explorer':
            return self._analyze_file_explorer_context(raw_text)
        else:
            return {'type': 'general', 'activity': 'unknown'}
    
    def _analyze_excel_context(self, text: str) -> Dict[str, Any]:
        """Analyze Excel-specific context."""
        context = {
            'type': 'spreadsheet',
            'activity': 'unknown',
            'operations': [],
            'data_indicators': []
        }
        
        # Detect Excel operations
        excel_operations = {
            'data_entry': ['entering', 'typing', 'input', 'data'],
            'formulas': ['=', 'sum(', 'average(', 'count(', 'if(', 'vlookup('],
            'formatting': ['bold', 'italic', 'underline', 'color', 'font'],
            'charts': ['chart', 'graph', 'pie', 'bar', 'line'],
            'filtering': ['filter', 'sort', 'ascending', 'descending'],
            'pivot': ['pivot', 'table', 'pivot table'],
            'calculation': ['calculate', 'compute', 'formula', 'function']
        }
        
        for operation, keywords in excel_operations.items():
            if any(keyword in text for keyword in keywords):
                context['operations'].append(operation)
        
        # Detect data patterns
        if re.search(r'[A-Z]\d+', text):  # Cell references like A1, B2
            context['data_indicators'].append('cell_references')
        if re.search(r'\d+\.\d+', text):  # Numbers
            context['data_indicators'].append('numeric_data')
        if 'table' in text:
            context['data_indicators'].append('table_data')
        
        # Determine primary activity
        if context['operations']:
            context['activity'] = context['operations'][0]
        else:
            context['activity'] = 'general_excel_usage'
        
        return context
    
    def _analyze_word_context(self, text: str) -> Dict[str, Any]:
        """Analyze Word-specific context."""
        context = {
            'type': 'document',
            'activity': 'unknown',
            'operations': []
        }
        
        word_operations = {
            'writing': ['typing', 'writing', 'text', 'document'],
            'formatting': ['bold', 'italic', 'underline', 'font', 'size'],
            'editing': ['edit', 'modify', 'change', 'update'],
            'reviewing': ['review', 'comment', 'track changes'],
            'inserting': ['insert', 'image', 'table', 'hyperlink']
        }
        
        for operation, keywords in word_operations.items():
            if any(keyword in text for keyword in keywords):
                context['operations'].append(operation)
        
        if context['operations']:
            context['activity'] = context['operations'][0]
        else:
            context['activity'] = 'general_word_usage'
        
        return context
    
    def _analyze_browser_context(self, text: str) -> Dict[str, Any]:
        """Analyze browser-specific context."""
        context = {
            'type': 'web_browser',
            'activity': 'unknown',
            'operations': []
        }
        
        browser_operations = {
            'browsing': ['http', 'www', 'com', 'org', 'net'],
            'searching': ['search', 'google', 'bing', 'yahoo'],
            'shopping': ['buy', 'cart', 'checkout', 'price', 'sale'],
            'social': ['facebook', 'twitter', 'instagram', 'linkedin'],
            'email': ['mail', 'gmail', 'outlook', 'yahoo mail']
        }
        
        for operation, keywords in browser_operations.items():
            if any(keyword in text for keyword in keywords):
                context['operations'].append(operation)
        
        if context['operations']:
            context['activity'] = context['operations'][0]
        else:
            context['activity'] = 'general_browsing'
        
        return context
    
    def _analyze_file_explorer_context(self, text: str) -> Dict[str, Any]:
        """Analyze file explorer context."""
        context = {
            'type': 'file_management',
            'activity': 'unknown',
            'operations': []
        }
        
        file_operations = {
            'organizing': ['folder', 'directory', 'organize', 'sort'],
            'copying': ['copy', 'duplicate', 'clone'],
            'moving': ['move', 'cut', 'paste', 'relocate'],
            'deleting': ['delete', 'remove', 'trash'],
            'renaming': ['rename', 'name', 'title']
        }
        
        for operation, keywords in file_operations.items():
            if any(keyword in text for keyword in keywords):
                context['operations'].append(operation)
        
        if context['operations']:
            context['activity'] = context['operations'][0]
        else:
            context['activity'] = 'general_file_management'
        
        return context
    
    def _detect_tasks(self, text_data: Dict[str, Any], ui_elements: Dict[str, List[str]], app_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect specific tasks being performed."""
        tasks = []
        raw_text = text_data['raw_text'].lower()
        
        # Task patterns
        task_patterns = {
            'data_entry': {
                'keywords': ['entering', 'typing', 'input', 'data', 'form', 'field'],
                'confidence': 0.8
            },
            'file_operations': {
                'keywords': ['save', 'open', 'close', 'file', 'document', 'folder'],
                'confidence': 0.7
            },
            'formatting': {
                'keywords': ['bold', 'italic', 'underline', 'color', 'font', 'size', 'format'],
                'confidence': 0.6
            },
            'navigation': {
                'keywords': ['click', 'select', 'navigate', 'menu', 'tab', 'button'],
                'confidence': 0.5
            },
            'calculation': {
                'keywords': ['calculate', 'formula', 'sum', 'average', 'count', '='],
                'confidence': 0.9
            },
            'searching': {
                'keywords': ['search', 'find', 'look', 'query', 'filter'],
                'confidence': 0.7
            }
        }
        
        for task_name, pattern in task_patterns.items():
            keyword_matches = sum(1 for keyword in pattern['keywords'] if keyword in raw_text)
            if keyword_matches > 0:
                confidence = min(pattern['confidence'] * keyword_matches, 1.0)
                tasks.append({
                    'name': task_name,
                    'confidence': confidence,
                    'keywords_found': [kw for kw in pattern['keywords'] if kw in raw_text],
                    'context': app_context.get('name', 'unknown')
                })
        
        return tasks
    
    def _calculate_confidence(self, text_data: Dict[str, Any], ui_elements: Dict[str, List[str]]) -> float:
        """Calculate overall confidence in the analysis."""
        confidence = 0.0
        
        # Base confidence from text quality
        if text_data['word_count'] > 0:
            confidence += 0.3
        
        # UI elements confidence
        total_ui_elements = sum(len(elements) for elements in ui_elements.values())
        if total_ui_elements > 0:
            confidence += min(total_ui_elements * 0.1, 0.4)
        
        # Application detection confidence
        if ui_elements['applications']:
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure."""
        return {
            'raw_text': '',
            'ui_elements': {
                'applications': [],
                'buttons': [],
                'menus': [],
                'tabs': [],
                'toolbars': [],
                'other': []
            },
            'application': {
                'name': 'unknown',
                'confidence': 0,
                'context': {'type': 'general', 'activity': 'unknown'}
            },
            'detected_tasks': [],
            'confidence': 0.0,
            'timestamp': 0
        }


# Compatibility function
def analyze_screenshot_with_ocr(image_path: str) -> Dict[str, Any]:
    """Convenience function for OCR analysis."""
    analyzer = OCRAnalyzer()
    return analyzer.analyze_screenshot(image_path)
