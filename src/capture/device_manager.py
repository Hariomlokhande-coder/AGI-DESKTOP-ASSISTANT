"""Enhanced device and permission management with comprehensive error handling."""
import os
import platform
import subprocess
import time
from typing import List, Dict, Optional, Tuple
import pyaudio
import mss
from ..error_handling.exceptions import DeviceError, PermissionError
from ..error_handling.logger import logger


class DeviceManager:
    """Enhanced device manager with comprehensive device detection and permission checking."""
    
    def __init__(self):
        self.audio_devices = []
        self.video_devices = []
        self.monitors = []
        self.available_audio = False
        self.available_video = False
        self.screen_capture_permission = False
        self.audio_permission = False
        self.system_info = self._get_system_info()
        self.last_device_check = 0
        self.device_check_interval = 30  # Check devices every 30 seconds
        
    def _get_system_info(self) -> Dict:
        """Get comprehensive system information."""
        try:
            import psutil
            
            return {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'disk_total': psutil.disk_usage('/').total if platform.system() != 'Windows' else psutil.disk_usage('C:').total
            }
        except Exception as e:
            logger.warning(f"Could not get complete system info: {e}")
            return {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'python_version': platform.python_version()
            }
    
    def _check_devices_if_needed(self) -> None:
        """Check devices if enough time has passed since last check."""
        current_time = time.time()
        if current_time - self.last_device_check > self.device_check_interval:
            self.check_all_devices()
            self.last_device_check = current_time
    
    def check_all_devices(self) -> Dict:
        """Check all available devices and permissions."""
        try:
            logger.info("Checking all devices and permissions...")
            
            # Check audio devices
            audio_devices = self.check_audio_devices()
            
            # Check video/monitor devices
            video_devices = self.check_video_devices()
            
            # Check permissions
            screen_permission = self.check_screen_capture_permission()
            audio_permission = self.check_audio_permissions()
            
            # Compile results
            results = {
                'audio_devices': audio_devices,
                'video_devices': video_devices,
                'screen_capture_permission': screen_permission,
                'audio_permission': audio_permission,
                'system_info': self.system_info,
                'timestamp': time.time()
            }
            
            logger.info(f"Device check complete - Audio: {len(audio_devices)}, Video: {len(video_devices)}, Screen: {screen_permission}, Audio: {audio_permission}")
            return results
            
        except Exception as e:
            logger.error(f"Error checking all devices: {e}", exc_info=True)
            return {
                'audio_devices': [],
                'video_devices': [],
                'screen_capture_permission': False,
                'audio_permission': False,
                'system_info': self.system_info,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def check_audio_devices(self) -> List[Dict]:
        """Check available audio input devices with comprehensive error handling."""
        try:
            logger.info("Checking audio input devices...")
            
            audio = pyaudio.PyAudio()
            device_count = audio.get_device_count()
            
            self.audio_devices = []
            for i in range(device_count):
                try:
                    device_info = audio.get_device_info_by_index(i)
                    
                    # Only include devices with input capability
                    if device_info['maxInputChannels'] > 0:
                        device_data = {
                            'index': i,
                            'name': device_info['name'],
                            'channels': device_info['maxInputChannels'],
                            'sample_rate': int(device_info['defaultSampleRate']),
                            'latency': device_info['defaultLowInputLatency'],
                            'host_api': device_info['hostApi'],
                            'is_default': False
                        }
                        
                        # Check if this is the default input device
                        try:
                            default_device = audio.get_default_input_device_info()
                            if default_device['index'] == i:
                                device_data['is_default'] = True
                        except Exception:
                            pass
                        
                        self.audio_devices.append(device_data)
                        
                except Exception as e:
                    logger.warning(f"Error getting info for audio device {i}: {e}")
                    continue
            
            audio.terminate()
            self.available_audio = len(self.audio_devices) > 0
            
            logger.info(f"Found {len(self.audio_devices)} audio input devices")
            return self.audio_devices
            
        except Exception as e:
            logger.error(f"Error checking audio devices: {e}", exc_info=True)
            self.available_audio = False
            return []
    
    def check_video_devices(self) -> List[Dict]:
        """Check available video/monitor devices."""
        try:
            logger.info("Checking video/monitor devices...")
            
            self.monitors = []
            with mss.mss() as sct:
                for i, monitor in enumerate(sct.monitors):
                    if i == 0:  # Skip the "All monitors" entry
                        continue
                    
                    monitor_data = {
                        'index': i,
                        'left': monitor['left'],
                        'top': monitor['top'],
                        'width': monitor['width'],
                        'height': monitor['height'],
                        'name': f"Monitor {i}",
                        'is_primary': i == 1  # Usually monitor 1 is primary
                    }
                    
                    self.monitors.append(monitor_data)
            
            self.available_video = len(self.monitors) > 0
            
            logger.info(f"Found {len(self.monitors)} monitors")
            return self.monitors
            
        except Exception as e:
            logger.error(f"Error checking video devices: {e}", exc_info=True)
            self.available_video = False
            return []
    
    def check_screen_capture_permission(self) -> bool:
        """Check screen capture permissions with comprehensive error handling."""
        try:
            logger.info("Checking screen capture permissions...")
            
            with mss.mss() as sct:
                # Try to capture a screenshot from the primary monitor
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                
                if screenshot is None:
                    logger.warning("Screen capture returned None")
                    self.screen_capture_permission = False
                    return False
                
                # Check if screenshot has content
                if screenshot.size == 0:
                    logger.warning("Screen capture returned empty image")
                    self.screen_capture_permission = False
                    return False
                
                logger.info("Screen capture permission granted")
                self.screen_capture_permission = True
                return True
                
        except PermissionError as e:
            logger.error(f"Screen capture permission denied: {e}")
            self.screen_capture_permission = False
            return False
        except Exception as e:
            logger.error(f"Error checking screen capture permission: {e}", exc_info=True)
            self.screen_capture_permission = False
            return False
    
    def check_audio_permissions(self) -> bool:
        """Check audio recording permissions."""
        try:
            logger.info("Checking audio recording permissions...")
            
            audio = pyaudio.PyAudio()
            
            # Try to get device count (this will fail if no permissions)
            device_count = audio.get_device_count()
            if device_count == 0:
                logger.warning("No audio devices available")
                self.audio_permission = False
                return False
            
            # Try to get default input device info
            try:
                default_device = audio.get_default_input_device_info()
                logger.info(f"Default audio input device: {default_device['name']}")
            except Exception as e:
                logger.warning(f"Could not get default audio device: {e}")
            
            audio.terminate()
            
            logger.info("Audio permissions check passed")
            self.audio_permission = True
            return True
            
        except Exception as e:
            logger.error(f"Audio permissions check failed: {e}", exc_info=True)
            self.audio_permission = False
            return False
    
    def get_default_audio_device(self) -> Optional[Dict]:
        """Get default audio input device with error handling."""
        try:
            self._check_devices_if_needed()
            
            if not self.audio_devices:
                logger.warning("No audio devices available")
                return None
            
            # Find the default device
            for device in self.audio_devices:
                if device.get('is_default', False):
                    logger.info(f"Found default audio device: {device['name']}")
                    return device
            
            # Fallback to first device
            default_device = self.audio_devices[0]
            logger.info(f"Using first available audio device: {default_device['name']}")
            return default_device
            
        except Exception as e:
            logger.error(f"Error getting default audio device: {e}")
            return None
    
    def get_primary_monitor(self) -> Optional[Dict]:
        """Get primary monitor information."""
        try:
            self._check_devices_if_needed()
            
            if not self.monitors:
                logger.warning("No monitors available")
                return None
            
            # Find the primary monitor
            for monitor in self.monitors:
                if monitor.get('is_primary', False):
                    logger.info(f"Found primary monitor: {monitor['width']}x{monitor['height']}")
                    return monitor
            
            # Fallback to first monitor
            primary_monitor = self.monitors[0]
            logger.info(f"Using first available monitor: {primary_monitor['width']}x{primary_monitor['height']}")
            return primary_monitor
            
        except Exception as e:
            logger.error(f"Error getting primary monitor: {e}")
            return None
    
    def test_audio_device(self, device_index: int, sample_rate: int = 16000, channels: int = 1) -> bool:
        """Test if a specific audio device works with given parameters."""
        try:
            logger.info(f"Testing audio device {device_index} with rate={sample_rate}, channels={channels}")
            
            audio = pyaudio.PyAudio()
            
            # Test if device supports the format
            is_supported = audio.is_format_supported(
                rate=sample_rate,
                input_device=device_index,
                input_channels=channels,
                input_format=pyaudio.paInt16
            )
            
            if not is_supported:
                logger.warning(f"Device {device_index} does not support the required format")
                audio.terminate()
                return False
            
            # Try to open a test stream
            try:
                stream = audio.open(
                    format=pyaudio.paInt16,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=1024
                )
                
                # Try to read a small amount of data
                test_data = stream.read(1024, exception_on_overflow=False)
                
                stream.stop_stream()
                stream.close()
                audio.terminate()
                
                if test_data:
                    logger.info(f"Audio device {device_index} test successful")
                    return True
                else:
                    logger.warning(f"Audio device {device_index} returned no data")
                    return False
                    
            except Exception as e:
                logger.error(f"Error testing audio device {device_index}: {e}")
                audio.terminate()
                return False
                
        except Exception as e:
            logger.error(f"Error testing audio device {device_index}: {e}")
            return False
    
    def test_screen_capture(self, monitor_index: int = 1) -> bool:
        """Test screen capture on a specific monitor."""
        try:
            logger.info(f"Testing screen capture on monitor {monitor_index}")
            
            with mss.mss() as sct:
                if monitor_index >= len(sct.monitors):
                    logger.error(f"Monitor index {monitor_index} out of range")
                    return False
                
                monitor = sct.monitors[monitor_index]
                screenshot = sct.grab(monitor)
                
                if screenshot is None or screenshot.size == 0:
                    logger.error(f"Screen capture test failed on monitor {monitor_index}")
                    return False
                
                logger.info(f"Screen capture test successful on monitor {monitor_index}")
                return True
                
        except Exception as e:
            logger.error(f"Error testing screen capture on monitor {monitor_index}: {e}")
            return False
    
    def get_device_status(self) -> Dict:
        """Get comprehensive device status."""
        try:
            self._check_devices_if_needed()
            
            return {
                'audio_devices_count': len(self.audio_devices),
                'video_devices_count': len(self.monitors),
                'audio_available': self.available_audio,
                'video_available': self.available_video,
                'screen_capture_permission': self.screen_capture_permission,
                'audio_permission': self.audio_permission,
                'system_info': self.system_info,
                'last_check': self.last_device_check
            }
            
        except Exception as e:
            logger.error(f"Error getting device status: {e}")
            return {
                'audio_devices_count': 0,
                'video_devices_count': 0,
                'audio_available': False,
                'video_available': False,
                'screen_capture_permission': False,
                'audio_permission': False,
                'error': str(e)
            }
    
    def get_permission_instructions(self) -> Dict:
        """Get platform-specific permission instructions."""
        try:
            platform_name = self.system_info.get('platform', 'Unknown').lower()
            
            instructions = {
                'windows': {
                    'screen_capture': [
                        "Run the application as Administrator",
                        "Check Windows Privacy Settings > Camera",
                        "Ensure no other applications are blocking screen capture"
                    ],
                    'audio': [
                        "Check Windows Privacy Settings > Microphone",
                        "Ensure microphone is not muted",
                        "Check Windows Sound Settings for input levels"
                    ]
                },
                'darwin': {  # macOS
                    'screen_capture': [
                        "Go to System Preferences > Security & Privacy > Privacy",
                        "Select 'Screen Recording' from the left sidebar",
                        "Add your application to the list and enable it",
                        "Restart the application after granting permission"
                    ],
                    'audio': [
                        "Go to System Preferences > Security & Privacy > Privacy",
                        "Select 'Microphone' from the left sidebar",
                        "Add your application to the list and enable it",
                        "Check System Preferences > Sound > Input for levels"
                    ]
                },
                'linux': {
                    'screen_capture': [
                        "Check if you're running in a desktop environment",
                        "Ensure X11 or Wayland is properly configured",
                        "Check for display server permissions",
                        "Try running with different display settings"
                    ],
                    'audio': [
                        "Check ALSA/PulseAudio configuration",
                        "Ensure microphone is not muted",
                        "Check audio input levels",
                        "Verify user is in audio group"
                    ]
                }
            }
            
            return instructions.get(platform_name, {
                'screen_capture': ["Check system documentation for screen capture permissions"],
                'audio': ["Check system documentation for audio recording permissions"]
            })
            
        except Exception as e:
            logger.error(f"Error getting permission instructions: {e}")
            return {
                'screen_capture': ["Unable to determine platform-specific instructions"],
                'audio': ["Unable to determine platform-specific instructions"]
            }
    
    def refresh_devices(self) -> Dict:
        """Force refresh of all device information."""
        try:
            logger.info("Refreshing all device information...")
            self.last_device_check = 0  # Force immediate check
            return self.check_all_devices()
            
        except Exception as e:
            logger.error(f"Error refreshing devices: {e}")
            return {
                'error': str(e),
                'timestamp': time.time()
            }
