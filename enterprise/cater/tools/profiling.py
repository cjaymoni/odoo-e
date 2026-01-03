"""
Performance Profiling and Logging Configuration for Catering Module
"""
import logging
import time
import functools
from contextlib import contextmanager

# Configure module logger
_logger = logging.getLogger(__name__)


def log_performance(func):
    """
    Decorator to log execution time of methods.
    
    Usage:
        @log_performance
        def my_method(self):
            # method implementation
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # Get class name if method is part of a class
        class_name = args[0].__class__.__name__ if args and hasattr(args[0], '__class__') else ''
        func_name = f"{class_name}.{func.__name__}" if class_name else func.__name__
        
        _logger.info(f"[PERFORMANCE] Starting {func_name}")
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log with different levels based on execution time
            if execution_time > 5:
                _logger.warning(f"[PERFORMANCE] {func_name} took {execution_time:.2f}s (SLOW)")
            elif execution_time > 1:
                _logger.info(f"[PERFORMANCE] {func_name} took {execution_time:.2f}s")
            else:
                _logger.debug(f"[PERFORMANCE] {func_name} took {execution_time:.2f}s")
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            _logger.error(f"[PERFORMANCE] {func_name} failed after {execution_time:.2f}s: {str(e)}")
            raise
    
    return wrapper


@contextmanager
def log_time_context(operation_name):
    """
    Context manager to log execution time of code blocks.
    
    Usage:
        with log_time_context("Complex calculation"):
            # code block
    """
    start_time = time.time()
    _logger.info(f"[PERFORMANCE] Starting: {operation_name}")
    
    try:
        yield
    finally:
        execution_time = time.time() - start_time
        if execution_time > 5:
            _logger.warning(f"[PERFORMANCE] {operation_name} took {execution_time:.2f}s (SLOW)")
        elif execution_time > 1:
            _logger.info(f"[PERFORMANCE] {operation_name} took {execution_time:.2f}s")
        else:
            _logger.debug(f"[PERFORMANCE] {operation_name} took {execution_time:.2f}s")


def log_method_call(log_args=False, log_result=False):
    """
    Decorator to log method calls with optional arguments and results.
    
    Usage:
        @log_method_call(log_args=True, log_result=True)
        def my_method(self, arg1, arg2):
            return result
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            class_name = args[0].__class__.__name__ if args and hasattr(args[0], '__class__') else ''
            func_name = f"{class_name}.{func.__name__}" if class_name else func.__name__
            
            log_msg = f"[CALL] {func_name}"
            
            if log_args:
                # Skip self/cls argument
                call_args = args[1:] if class_name else args
                log_msg += f" args={call_args}, kwargs={kwargs}"
            
            _logger.info(log_msg)
            
            try:
                result = func(*args, **kwargs)
                
                if log_result:
                    _logger.info(f"[CALL] {func_name} returned: {result}")
                
                return result
            except Exception as e:
                _logger.error(f"[CALL] {func_name} raised {type(e).__name__}: {str(e)}")
                raise
        
        return wrapper
    return decorator


def log_database_queries(func):
    """
    Decorator to log database query count for a method.
    Requires odoo.tools.config to be imported.
    
    Usage:
        @log_database_queries
        def my_method(self):
            # method implementation
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not args or not hasattr(args[0], 'env'):
            # Not an Odoo method, skip query counting
            return func(*args, **kwargs)
        
        self = args[0]
        cr = self.env.cr
        
        class_name = self.__class__.__name__
        func_name = f"{class_name}.{func.__name__}"
        
        # Get initial query count
        initial_count = cr.sql_log_count if hasattr(cr, 'sql_log_count') else 0
        
        try:
            result = func(*args, **kwargs)
            
            # Get final query count
            final_count = cr.sql_log_count if hasattr(cr, 'sql_log_count') else 0
            query_count = final_count - initial_count
            
            if query_count > 100:
                _logger.warning(f"[DB] {func_name} executed {query_count} queries (HIGH)")
            elif query_count > 50:
                _logger.info(f"[DB] {func_name} executed {query_count} queries")
            else:
                _logger.debug(f"[DB] {func_name} executed {query_count} queries")
            
            return result
        except Exception as e:
            _logger.error(f"[DB] {func_name} failed: {str(e)}")
            raise
    
    return wrapper


class PerformanceLogger:
    """
    Context manager for more detailed performance logging with nested sections.
    
    Usage:
        with PerformanceLogger("Main operation") as perf:
            # do something
            
            with perf.section("Sub-operation 1"):
                # do sub-operation
            
            with perf.section("Sub-operation 2"):
                # do another sub-operation
    """
    
    def __init__(self, operation_name):
        self.operation_name = operation_name
        self.start_time = None
        self.sections = []
    
    def __enter__(self):
        self.start_time = time.time()
        _logger.info(f"[PERF] Starting: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        total_time = time.time() - self.start_time
        
        if exc_type:
            _logger.error(f"[PERF] {self.operation_name} failed after {total_time:.2f}s")
        else:
            _logger.info(f"[PERF] {self.operation_name} completed in {total_time:.2f}s")
            
            if self.sections:
                _logger.info(f"[PERF] Section breakdown:")
                for section_name, section_time in self.sections:
                    percentage = (section_time / total_time) * 100 if total_time > 0 else 0
                    _logger.info(f"[PERF]   - {section_name}: {section_time:.2f}s ({percentage:.1f}%)")
    
    @contextmanager
    def section(self, section_name):
        """Log a subsection of the operation"""
        start_time = time.time()
        _logger.debug(f"[PERF]   Starting section: {section_name}")
        
        try:
            yield
        finally:
            section_time = time.time() - start_time
            self.sections.append((section_name, section_time))
            _logger.debug(f"[PERF]   Section {section_name} took {section_time:.2f}s")


# Convenience function to enable debug logging
def enable_debug_logging():
    """Enable debug-level logging for the catering module"""
    logger = logging.getLogger('odoo.addons.cater')
    logger.setLevel(logging.DEBUG)
    _logger.info("Debug logging enabled for catering module")


# Convenience function to enable performance logging
def enable_performance_logging():
    """Enable performance logging"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    _logger.info("Performance logging enabled")
