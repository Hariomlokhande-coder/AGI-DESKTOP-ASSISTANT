"""
Comprehensive debugging and error handling system for AGE Agent.
"""

import os
import sys
import traceback
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from .simple_logger import logger


class DebugSystem:
    """Comprehensive debugging system for AGE Agent."""
    
    def __init__(self):
        self.debug_info = {}
        self.error_history = []
        self.performance_metrics = {}
        self.system_checks = {}
        logger.info("DebugSystem initialized")
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log detailed error information."""
        try:
            error_info = {
                "timestamp": datetime.now().isoformat(),
                "error_type": type(error).__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc(),
                "context": context or {},
                "system_info": self._get_system_info()
            }
            
            self.error_history.append(error_info)
            logger.error(f"Error logged: {error_info['error_type']} - {error_info['error_message']}")
            
            return error_info
            
        except Exception as e:
            logger.error(f"Failed to log error: {e}")
            return None
    
    def check_system_health(self) -> Dict[str, Any]:
        """Perform comprehensive system health check."""
        try:
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "healthy",
                "checks": {}
            }
            
            # Check Python environment
            health_status["checks"]["python_version"] = {
                "status": "ok",
                "value": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "details": "Python version is compatible"
            }
            
            # Check required modules
            required_modules = [
                "PyQt5", "mss", "cv2", "numpy", "psutil", 
                "yaml", "dotenv", "requests", "json"
            ]
            
            missing_modules = []
            for module in required_modules:
                try:
                    __import__(module)
                    health_status["checks"][f"module_{module}"] = {
                        "status": "ok",
                        "details": f"Module {module} is available"
                    }
                except ImportError:
                    missing_modules.append(module)
                    health_status["checks"][f"module_{module}"] = {
                        "status": "error",
                        "details": f"Module {module} is missing"
                    }
            
            if missing_modules:
                health_status["overall_status"] = "degraded"
                health_status["missing_modules"] = missing_modules
            
            # Check file system
            health_status["checks"]["file_system"] = self._check_file_system()
            
            # Check memory usage
            health_status["checks"]["memory"] = self._check_memory_usage()
            
            # Check disk space
            health_status["checks"]["disk_space"] = self._check_disk_space()
            
            # Check configuration
            health_status["checks"]["configuration"] = self._check_configuration()
            
            self.system_checks = health_status
            return health_status
            
        except Exception as e:
            logger.error(f"System health check failed: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "error",
                "error": str(e)
            }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        try:
            import platform
            import psutil
            
            return {
                "platform": platform.platform(),
                "python_version": sys.version,
                "architecture": platform.architecture(),
                "processor": platform.processor(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
                "working_directory": os.getcwd(),
                "python_path": sys.path[:5]  # First 5 paths
            }
        except Exception as e:
            return {"error": f"Failed to get system info: {e}"}
    
    def _check_file_system(self) -> Dict[str, Any]:
        """Check file system health."""
        try:
            # Check if required directories exist
            required_dirs = [
                "user_data", "user_data/screenshots", "user_data/audio", 
                "user_data/processed", "logs"
            ]
            
            missing_dirs = []
            for dir_path in required_dirs:
                if not os.path.exists(dir_path):
                    missing_dirs.append(dir_path)
            
            if missing_dirs:
                return {
                    "status": "warning",
                    "details": f"Missing directories: {missing_dirs}",
                    "missing_dirs": missing_dirs
                }
            else:
                return {
                    "status": "ok",
                    "details": "All required directories exist"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "details": f"File system check failed: {e}"
            }
    
    def _check_memory_usage(self) -> Dict[str, Any]:
        """Check memory usage."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            usage_percent = memory.percent
            if usage_percent > 90:
                status = "critical"
            elif usage_percent > 80:
                status = "warning"
            else:
                status = "ok"
            
            return {
                "status": status,
                "usage_percent": usage_percent,
                "available_gb": round(memory.available / (1024**3), 2),
                "total_gb": round(memory.total / (1024**3), 2)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "details": f"Memory check failed: {e}"
            }
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space."""
        try:
            import psutil
            
            # Check disk usage
            if os.name == 'nt':  # Windows
                disk_usage = psutil.disk_usage('C:')
            else:  # Unix-like
                disk_usage = psutil.disk_usage('/')
            
            usage_percent = disk_usage.percent
            if usage_percent > 95:
                status = "critical"
            elif usage_percent > 85:
                status = "warning"
            else:
                status = "ok"
            
            return {
                "status": status,
                "usage_percent": usage_percent,
                "free_gb": round(disk_usage.free / (1024**3), 2),
                "total_gb": round(disk_usage.total / (1024**3), 2)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "details": f"Disk space check failed: {e}"
            }
    
    def _check_configuration(self) -> Dict[str, Any]:
        """Check configuration health."""
        try:
            from ..storage.simple_config import config
            
            # Check if config is accessible
            test_value = config.get('recording.fps', None)
            
            return {
                "status": "ok",
                "details": "Configuration is accessible",
                "sample_value": test_value
            }
            
        except Exception as e:
            return {
                "status": "error",
                "details": f"Configuration check failed: {e}"
            }
    
    def get_debug_report(self) -> Dict[str, Any]:
        """Generate comprehensive debug report."""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "system_health": self.check_system_health(),
                "error_history": self.error_history[-10:],  # Last 10 errors
                "performance_metrics": self.performance_metrics,
                "debug_info": self.debug_info,
                "recommendations": self._generate_recommendations()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate debug report: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": f"Debug report generation failed: {e}"
            }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on system state."""
        recommendations = []
        
        # Check system health
        if self.system_checks:
            overall_status = self.system_checks.get("overall_status", "unknown")
            if overall_status == "degraded":
                recommendations.append("Install missing modules to improve functionality")
            
            # Check memory
            memory_check = self.system_checks.get("checks", {}).get("memory", {})
            if memory_check.get("status") == "warning":
                recommendations.append("Close unnecessary applications to free up memory")
            elif memory_check.get("status") == "critical":
                recommendations.append("Restart the application to free up memory")
            
            # Check disk space
            disk_check = self.system_checks.get("checks", {}).get("disk_space", {})
            if disk_check.get("status") == "warning":
                recommendations.append("Free up disk space to prevent storage issues")
            elif disk_check.get("status") == "critical":
                recommendations.append("Urgent: Free up disk space immediately")
        
        # Check error history
        if len(self.error_history) > 5:
            recommendations.append("High error count detected - review error logs")
        
        if not recommendations:
            recommendations.append("System appears to be running normally")
        
        return recommendations
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = ""):
        """Log performance metrics."""
        try:
            if metric_name not in self.performance_metrics:
                self.performance_metrics[metric_name] = []
            
            self.performance_metrics[metric_name].append({
                "timestamp": datetime.now().isoformat(),
                "value": value,
                "unit": unit
            })
            
            # Keep only last 100 entries per metric
            if len(self.performance_metrics[metric_name]) > 100:
                self.performance_metrics[metric_name] = self.performance_metrics[metric_name][-100:]
                
        except Exception as e:
            logger.error(f"Failed to log performance metric: {e}")
    
    def save_debug_report(self, filepath: str = None):
        """Save debug report to file."""
        try:
            if filepath is None:
                filepath = f"logs/debug_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            report = self.get_debug_report()
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Debug report saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save debug report: {e}")
            return None


# Global debug system instance
debug_system = DebugSystem()
