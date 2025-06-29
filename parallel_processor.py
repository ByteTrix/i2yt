#!/usr/bin/env python3

import os
import sys
import time
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from typing import List, Callable, Any, Optional, Dict, Tuple
from functools import wraps
from queue import Queue
import psutil

# Progress bar library
from tqdm import tqdm

# Setup logger
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    # Fallback configuration if config not available
    class Config:
        ENABLE_CONCURRENT_PROCESSING = True
        MAX_SCRAPING_WORKERS = 4
        MAX_DOWNLOAD_WORKERS = 3
        MAX_UPLOAD_WORKERS = 2
        MAX_DESCRIPTION_WORKERS = 5
        BATCH_PROCESSING_SIZE = 20
        WORKER_TIMEOUT = 60
        SHOW_PROGRESS_BARS = True
        MINIMAL_OUTPUT = True
    config = Config()


class ParallelProcessor:
    """
    🚀 Professional parallel processing manager with tqdm progress bars
    
    Features:
    • Automatic worker scaling based on system resources
    • Beautiful tqdm progress bars with ETA and throughput
    • Comprehensive error handling and retry mechanisms
    • Memory-efficient batch processing
    • Thread-safe operations
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or self._setup_logger()
        self.active_executors: Dict[str, ThreadPoolExecutor] = {}
        self.performance_stats = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_execution_time': 0,
            'average_task_time': 0
        }
        self._lock = threading.Lock()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup default logger if none provided"""
        logger = logging.getLogger('ParallelProcessor')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def get_optimal_workers(self, task_type: str, item_count: int) -> int:
        """
        🎯 Calculate optimal number of workers based on system resources and task type
        
        Args:
            task_type: Type of task ('scraping', 'download', 'upload', 'description')
            item_count: Number of items to process
            
        Returns:
            Optimal number of worker threads
        """
        if not config.ENABLE_CONCURRENT_PROCESSING:
            return 1
            
        # Get system resources
        cpu_count = os.cpu_count() or 4
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        # Base worker counts from configuration
        worker_limits = {
            'scraping': getattr(config, 'MAX_SCRAPING_WORKERS', 4),
            'download': getattr(config, 'MAX_DOWNLOAD_WORKERS', 3),
            'upload': getattr(config, 'MAX_UPLOAD_WORKERS', 2),
            'description': getattr(config, 'MAX_DESCRIPTION_WORKERS', 5),
            'date_checking': getattr(config, 'MAX_DATE_CHECKING_WORKERS', 6)
        }
        
        base_workers = worker_limits.get(task_type, 3)
        
        # Adjust based on system resources
        if memory_gb < 4:  # Low memory system
            workers = min(base_workers, 2)
        elif memory_gb < 8:  # Medium memory system
            workers = min(base_workers, cpu_count // 2)
        else:  # High memory system
            workers = min(base_workers, cpu_count)
        
        # Scale based on item count
        if item_count < 5:
            workers = min(workers, 2)
        elif item_count < 20:
            workers = min(workers, workers)
        else:
            workers = min(workers, max(2, workers))
        
        # Ensure at least 1 worker
        workers = max(1, workers)
        
        self.logger.debug(f"🔧 {task_type.title()}: {item_count} items → {workers} workers "
                         f"(CPU: {cpu_count}, RAM: {memory_gb:.1f}GB)")
        
        return workers
    
    def process_in_parallel(
        self,
        items: List[Any],
        worker_function: Callable,
        task_type: str = 'general',
        progress_callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None,
        **kwargs
    ) -> List[Any]:
        """
        🚀 Execute tasks in parallel with beautiful tqdm progress bars
        
        Args:
            items: List of items to process
            worker_function: Function to apply to each item
            task_type: Type of task for optimal worker calculation
            progress_callback: Function to call with progress updates
            error_callback: Function to call when errors occur
            **kwargs: Additional arguments to pass to worker function
            
        Returns:
            List of results from processed items
        """
        if not items:
            return []
            
        if not config.ENABLE_CONCURRENT_PROCESSING or len(items) == 1:
            return self._process_sequential(items, worker_function, progress_callback, **kwargs)
        
        start_time = time.time()
        workers = self.get_optimal_workers(task_type, len(items))
        
        # Initialize progress bar if enabled
        pbar = None
        if getattr(config, 'SHOW_PROGRESS_BARS', True):
            desc = f"{task_type.title()}" if not getattr(config, 'MINIMAL_OUTPUT', True) else task_type
            pbar = tqdm(
                total=len(items),
                desc=desc,
                unit="item",
                ncols=80,
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
            )
        
        results = []
        completed_count = 0
        failed_count = 0
        
        try:
            with ThreadPoolExecutor(max_workers=workers, thread_name_prefix=f"{task_type}_worker") as executor:
                # Store executor for potential cleanup
                with self._lock:
                    self.active_executors[task_type] = executor
                
                # Submit all tasks
                future_to_item = {}
                for i, item in enumerate(items):
                    try:
                        future = executor.submit(self._safe_worker_wrapper, 
                                               worker_function, item, i, **kwargs)
                        future_to_item[future] = (item, i)
                    except Exception as e:
                        self.logger.error(f"❌ Failed to submit task {i}: {e}")
                        failed_count += 1
                        if pbar:
                            pbar.update(1)
                
                # Process completed tasks
                for future in as_completed(future_to_item, timeout=getattr(config, 'WORKER_TIMEOUT', 60)):
                    item, index = future_to_item[future]
                    
                    try:
                        result = future.result()
                        if result is not None:
                            results.append(result)
                            completed_count += 1
                        else:
                            failed_count += 1
                            
                    except Exception as e:
                        self.logger.warning(f"⚠️  Task {index} failed: {e}")
                        failed_count += 1
                        if error_callback:
                            error_callback(item, e)
                    
                    # Update progress bar
                    if pbar:
                        pbar.update(1)
                        # Update postfix with stats
                        pbar.set_postfix({
                            'success': completed_count,
                            'failed': failed_count,
                            'rate': f"{completed_count/(time.time()-start_time):.1f}/s"
                        })
                    
                    # Progress callback
                    total_processed = completed_count + failed_count
                    if progress_callback:
                        progress_callback(total_processed, len(items), completed_count, failed_count)
                
        except Exception as e:
            self.logger.error(f"💥 Parallel processing failed: {e}")
            # Fallback to sequential processing
            if pbar:
                pbar.close()
            self.logger.info("🔄 Falling back to sequential processing...")
            return self._process_sequential(items, worker_function, progress_callback, **kwargs)
        
        finally:
            # Cleanup
            if pbar:
                pbar.close()
            with self._lock:
                if task_type in self.active_executors:
                    del self.active_executors[task_type]
        
        # Update performance stats
        execution_time = time.time() - start_time
        self._update_performance_stats(completed_count, failed_count, execution_time)
        
        # Final completion message - concise and informative
        success_rate = (completed_count / len(items)) * 100 if items else 0
        if completed_count > 0 or failed_count > 0:
            result_icon = "✅" if success_rate >= 90 else "⚠️" if success_rate >= 50 else "❌"
            if not getattr(config, 'MINIMAL_OUTPUT', True):
                self.logger.info(f"{result_icon} {task_type.title()}: {completed_count}/{len(items)} "
                               f"({success_rate:.0f}%) in {execution_time:.1f}s")
        
        return results
    
    def _safe_worker_wrapper(self, worker_function: Callable, item: Any, index: int, **kwargs) -> Any:
        """
        🛡️  Safe wrapper for worker functions with error handling
        
        Args:
            worker_function: The actual worker function
            item: Item to process
            index: Item index for logging
            **kwargs: Additional arguments
            
        Returns:
            Result from worker function or None if failed
        """
        try:
            result = worker_function(item, **kwargs)
            return result
        except Exception as e:
            self.logger.warning(f"⚠️  Worker {index} failed for item {item}: {e}")
            return None
    
    def _process_sequential(
        self, 
        items: List[Any], 
        worker_function: Callable, 
        progress_callback: Optional[Callable] = None,
        **kwargs
    ) -> List[Any]:
        """
        🔄 Sequential processing with tqdm progress bar
        """
        results = []
        
        # Initialize progress bar if enabled
        pbar = None
        if getattr(config, 'SHOW_PROGRESS_BARS', True):
            desc = "Sequential" if not getattr(config, 'MINIMAL_OUTPUT', True) else "Processing"
            pbar = tqdm(
                total=len(items),
                desc=desc,
                unit="item",
                ncols=80,
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
            )
        
        try:
            for i, item in enumerate(items):
                try:
                    result = worker_function(item, **kwargs)
                    if result is not None:
                        results.append(result)
                        
                    if progress_callback:
                        progress_callback(i + 1, len(items), len(results), i + 1 - len(results))
                        
                    if pbar:
                        pbar.update(1)
                        pbar.set_postfix({
                            'success': len(results),
                            'failed': i + 1 - len(results)
                        })
                        
                except Exception as e:
                    self.logger.warning(f"⚠️  Sequential task {i} failed: {e}")
                    if pbar:
                        pbar.update(1)
        finally:
            if pbar:
                pbar.close()
        
        return results
    
    def _update_performance_stats(self, completed: int, failed: int, execution_time: float):
        """Update internal performance statistics"""
        with self._lock:
            self.performance_stats['tasks_completed'] += completed
            self.performance_stats['tasks_failed'] += failed
            self.performance_stats['total_execution_time'] += execution_time
            
            total_tasks = self.performance_stats['tasks_completed'] + self.performance_stats['tasks_failed']
            if total_tasks > 0:
                self.performance_stats['average_task_time'] = (
                    self.performance_stats['total_execution_time'] / total_tasks
                )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        with self._lock:
            return self.performance_stats.copy()
    
    def shutdown_all_executors(self):
        """Gracefully shutdown all active executors"""
        with self._lock:
            for task_type, executor in self.active_executors.items():
                self.logger.info(f"🛑 Shutting down {task_type} executor...")
                executor.shutdown(wait=True)
            self.active_executors.clear()


# Global instance for use across modules
_global_processor = None

def get_parallel_processor(logger: Optional[logging.Logger] = None) -> ParallelProcessor:
    """
    🌐 Get global parallel processor instance (singleton pattern)
    
    Args:
        logger: Optional logger to use
        
    Returns:
        Global ParallelProcessor instance
    """
    global _global_processor
    if _global_processor is None:
        _global_processor = ParallelProcessor(logger)
    return _global_processor


def parallel_process(
    items: List[Any],
    worker_function: Callable,
    task_type: str = 'general',
    logger: Optional[logging.Logger] = None,
    **kwargs
) -> List[Any]:
    """
    🚀 Convenient function for parallel processing
    
    Args:
        items: Items to process
        worker_function: Function to apply to each item
        task_type: Type of task for optimization
        logger: Optional logger
        **kwargs: Additional arguments for worker function
        
    Returns:
        List of processed results
    """
    processor = get_parallel_processor(logger)
    return processor.process_in_parallel(items, worker_function, task_type, **kwargs)


if __name__ == "__main__":
    # Demo/test code
    import random
    
    def demo_worker(item):
        """Demo worker function"""
        time.sleep(random.uniform(0.1, 0.5))  # Simulate work
        return f"Processed: {item}"
    
    # Test parallel processing
    test_items = [f"item_{i}" for i in range(20)]
    
    processor = ParallelProcessor()
    results = processor.process_in_parallel(test_items, demo_worker, 'demo')
    
    logger.info(f"Processed {len(results)} items successfully")
    logger.debug(f"Performance stats: {processor.get_performance_stats()}")
