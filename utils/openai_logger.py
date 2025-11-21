import logging
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from functools import wraps
import asyncio
import os


class OpenAITimingLogger:
    """Logger specifically for tracking OpenAI API call timings and metrics"""
    
    def __init__(self, log_file: str = "logs/openai-timing.log"):
        self.log_file = log_file
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up the timing logger with proper formatting"""
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        logger = logging.getLogger('openai_timing')
        logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if not logger.handlers:
            # Create file handler
            handler = logging.FileHandler(self.log_file, encoding='utf-8')
            handler.setLevel(logging.INFO)
            
            # Create detailed formatter
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            
            logger.addHandler(handler)
            logger.propagate = False
        
        return logger
    
    def log_api_call(self, 
                    function_name: str,
                    model: str,
                    duration: float,
                    tokens_used: Optional[int] = None,
                    success: bool = True,
                    error_message: Optional[str] = None,
                    request_size: Optional[int] = None,
                    **extra_data) -> None:
        """
        Log OpenAI API call with timing and metrics
        
        Args:
            function_name: Name of the calling function
            model: OpenAI model used
            duration: Time taken in seconds
            tokens_used: Number of tokens consumed
            success: Whether the call was successful
            error_message: Error message if call failed
            request_size: Size of the request payload
            extra_data: Additional data to log
        """
        
        log_data = {
            'function': function_name,
            'model': model,
            'duration_seconds': round(duration, 3),
            'duration_ms': round(duration * 1000, 1),
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        if tokens_used is not None:
            log_data['tokens_used'] = tokens_used
            log_data['tokens_per_second'] = round(tokens_used / duration, 2) if duration > 0 else 0
        
        if request_size is not None:
            log_data['request_size_chars'] = request_size
        
        if error_message:
            log_data['error'] = error_message
        
        # Add any extra data
        log_data.update(extra_data)
        
        # Create readable log message
        status = "SUCCESS" if success else "FAILED"
        message_parts = [
            f"OpenAI API Call [{status}]",
            f"Function: {function_name}",
            f"Model: {model}",
            f"Duration: {log_data['duration_seconds']}s"
        ]
        
        if tokens_used is not None:
            message_parts.append(f"Tokens: {tokens_used}")
            message_parts.append(f"Rate: {log_data['tokens_per_second']}/s")
        
        if error_message:
            message_parts.append(f"Error: {error_message}")
        
        log_message = " | ".join(message_parts)
        
        # Log with structured data
        if success:
            self.logger.info(f"{log_message} | Data: {json.dumps(log_data, separators=(',', ':'))}")
        else:
            self.logger.error(f"{log_message} | Data: {json.dumps(log_data, separators=(',', ':'))}")
    
    def log_batch_summary(self, batch_data: List[Dict[str, Any]]) -> None:
        """Log summary of multiple API calls"""
        if not batch_data:
            return
        
        total_calls = len(batch_data)
        total_duration = sum(call.get('duration_seconds', 0) for call in batch_data)
        total_tokens = sum(call.get('tokens_used', 0) for call in batch_data if call.get('tokens_used'))
        successful_calls = sum(1 for call in batch_data if call.get('success', True))
        
        summary = {
            'batch_summary': True,
            'total_calls': total_calls,
            'successful_calls': successful_calls,
            'failed_calls': total_calls - successful_calls,
            'total_duration_seconds': round(total_duration, 3),
            'average_duration_seconds': round(total_duration / total_calls, 3) if total_calls > 0 else 0,
            'total_tokens': total_tokens,
            'average_tokens_per_call': round(total_tokens / total_calls, 1) if total_calls > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"Batch Summary | {json.dumps(summary, separators=(',', ':'))}")


# Global logger instance
openai_timing_logger = OpenAITimingLogger()


def log_openai_timing(function_name: Optional[str] = None):
    """
    Decorator to automatically log OpenAI API call timings
    
    Usage:
        @log_openai_timing("generate_lesson_plan")
        async def some_openai_function():
            # OpenAI API call here
            pass
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            func_name = function_name or func.__name__
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Try to extract model info from args/kwargs if available
                model = "unknown"
                if hasattr(args[0], 'config') and hasattr(args[0].config, 'model_name'):
                    model = args[0].config.model_name
                
                # Extract additional info from result if it's a tuple with success status
                success = True
                error_msg = None
                if isinstance(result, tuple) and len(result) >= 3:
                    success = result[0]
                    if not success:
                        error_msg = result[2]
                
                openai_timing_logger.log_api_call(
                    function_name=func_name,
                    model=model,
                    duration=duration,
                    success=success,
                    error_message=error_msg
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Try to get model info
                model = "unknown"
                if args and hasattr(args[0], 'config') and hasattr(args[0].config, 'model_name'):
                    model = args[0].config.model_name
                
                openai_timing_logger.log_api_call(
                    function_name=func_name,
                    model=model,
                    duration=duration,
                    success=False,
                    error_message=str(e)
                )
                
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            func_name = function_name or func.__name__
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Try to extract model info
                model = "unknown"
                if hasattr(args[0], 'config') and hasattr(args[0].config, 'model_name'):
                    model = args[0].config.model_name
                
                openai_timing_logger.log_api_call(
                    function_name=func_name,
                    model=model,
                    duration=duration,
                    success=True
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Try to get model info
                model = "unknown"
                if args and hasattr(args[0], 'config') and hasattr(args[0].config, 'model_name'):
                    model = args[0].config.model_name
                
                openai_timing_logger.log_api_call(
                    function_name=func_name,
                    model=model,
                    duration=duration,
                    success=False,
                    error_message=str(e)
                )
                
                raise
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator