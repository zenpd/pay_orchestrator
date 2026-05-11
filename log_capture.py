"""
Log Capture Utility - Capture processing logs for UI display
"""

import io
import sys
from contextlib import contextmanager
from datetime import datetime
from threading import Lock

class LogCapture:
    """Thread-safe log capture for displaying in UI"""
    
    def __init__(self):
        self.logs = {}
        self.lock = Lock()
    
    def create_capture(self, payment_id: str):
        """Create a new log capture for a payment"""
        with self.lock:
            self.logs[payment_id] = {
                "logs": [],
                "start_time": datetime.now().isoformat(),
                "status": "PROCESSING"
            }
    
    def add_log(self, payment_id: str, message: str, level: str = "INFO"):
        """Add a log message"""
        with self.lock:
            if payment_id in self.logs:
                self.logs[payment_id]["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "level": level,
                    "message": message
                })
    
    def get_logs(self, payment_id: str):
        """Get logs for a payment"""
        with self.lock:
            return self.logs.get(payment_id, {"logs": [], "status": "NOT_FOUND"})
    
    def finalize(self, payment_id: str, status: str):
        """Finalize log capture"""
        with self.lock:
            if payment_id in self.logs:
                self.logs[payment_id]["status"] = status
                self.logs[payment_id]["end_time"] = datetime.now().isoformat()
    
    def cleanup_old(self, max_age_seconds: int = 3600):
        """Cleanup old logs (older than max_age_seconds)"""
        with self.lock:
            current_time = datetime.now()
            to_remove = []
            
            for payment_id, data in self.logs.items():
                start_time = datetime.fromisoformat(data["start_time"])
                age = (current_time - start_time).total_seconds()
                
                if age > max_age_seconds:
                    to_remove.append(payment_id)
            
            for payment_id in to_remove:
                del self.logs[payment_id]

# Global instance
_log_capture = None

def get_log_capture() -> LogCapture:
    """Get or create global log capture instance"""
    global _log_capture
    if _log_capture is None:
        _log_capture = LogCapture()
    return _log_capture

@contextmanager
def capture_logs(payment_id: str):
    """Context manager to capture stdout for a payment"""
    log_capture = get_log_capture()
    log_capture.create_capture(payment_id)
    
    # Capture stdout
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = LoggingIO(payment_id, log_capture, "INFO")
    sys.stderr = LoggingIO(payment_id, log_capture, "ERROR")
    
    try:
        yield log_capture
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

class LoggingIO(io.StringIO):
    """IO wrapper that captures to log capture"""
    
    def __init__(self, payment_id: str, log_capture: LogCapture, level: str):
        super().__init__()
        self.payment_id = payment_id
        self.log_capture = log_capture
        self.level = level
    
    def write(self, message: str):
        """Write message to log capture"""
        if message and message.strip():
            self.log_capture.add_log(self.payment_id, message.strip(), self.level)
        return len(message)
