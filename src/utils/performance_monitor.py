"""
Performance monitoring module for the Chicken Farm App.
This module provides functions to monitor and analyze application performance.
"""

import time
import os
import json
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from functools import wraps

# Try to import psutil but don't fail if it's not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Import logger if available, otherwise create a simple print function
try:
    from src.utils.error_handler import logger
except ImportError:
    class SimpleLogger:
        def debug(self, msg): print(f"DEBUG: {msg}")
        def info(self, msg): print(f"INFO: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")

    logger = SimpleLogger()


class PerformanceMetric:
    """Class to represent a performance metric."""

    def __init__(self, name: str, value: float, timestamp: float = None):
        """
        Initialize a performance metric.

        Args:
            name: Metric name
            value: Metric value
            timestamp: Timestamp (default: current time)
        """
        self.name = name
        self.value = value
        self.timestamp = timestamp or time.time()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert metric to dictionary.

        Returns:
            Dict representation of the metric
        """
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp
        }


class PerformanceMonitor:
    """Class to monitor application performance."""

    def __init__(self, metrics_dir: str = "metrics"):
        """
        Initialize the performance monitor.

        Args:
            metrics_dir: Directory to store metrics
        """
        self.metrics_dir = metrics_dir
        self.metrics: List[PerformanceMetric] = []
        self.start_time = time.time()
        self.monitoring = False
        self.monitor_thread = None

        # Create metrics directory if it doesn't exist
        os.makedirs(self.metrics_dir, exist_ok=True)

    def add_metric(self, name: str, value: float) -> None:
        """
        Add a performance metric.

        Args:
            name: Metric name
            value: Metric value
        """
        metric = PerformanceMetric(name, value)
        self.metrics.append(metric)
        logger.debug(f"Added performance metric: {name} = {value}")

    def get_metrics(self) -> List[Dict[str, Any]]:
        """
        Get all metrics.

        Returns:
            List of metrics as dictionaries
        """
        return [metric.to_dict() for metric in self.metrics]

    def clear_metrics(self) -> None:
        """Clear all metrics."""
        self.metrics = []

    def save_metrics(self, filename: str = None) -> str:
        """
        Save metrics to a JSON file.

        Args:
            filename: Optional filename

        Returns:
            Path to the saved file
        """
        if not self.metrics:
            return ""

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"metrics_{timestamp}.json"

        filepath = os.path.join(self.metrics_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.get_metrics(), f, ensure_ascii=False, indent=2)

            logger.info(f"Saved performance metrics to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving performance metrics: {e}")
            return ""

    def start_monitoring(self, interval: float = 5.0) -> None:
        """
        Start periodic monitoring of system resources.

        Args:
            interval: Monitoring interval in seconds
        """
        if self.monitoring or not PSUTIL_AVAILABLE:
            # If psutil is not available, just record basic metrics
            if not PSUTIL_AVAILABLE:
                logger.info("psutil not available, only basic metrics will be recorded")
                self.add_metric("app_start_time", time.time())
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_resources, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        logger.info(f"Started performance monitoring with interval {interval} seconds")

    def stop_monitoring(self) -> None:
        """Stop periodic monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
            self.monitor_thread = None

        # Record app runtime even if psutil is not available
        runtime = time.time() - self.start_time
        self.add_metric("app_runtime_seconds", runtime)

        logger.info("Stopped performance monitoring")

    def _monitor_resources(self, interval: float) -> None:
        """
        Monitor system resources periodically.

        Args:
            interval: Monitoring interval in seconds
        """
        if not PSUTIL_AVAILABLE:
            return

        while self.monitoring:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=0.1)
                self.add_metric("cpu_percent", cpu_percent)

                # Memory usage
                memory = psutil.virtual_memory()
                self.add_metric("memory_percent", memory.percent)
                self.add_metric("memory_used_mb", memory.used / (1024 * 1024))

                # Disk usage
                disk = psutil.disk_usage('/')
                self.add_metric("disk_percent", disk.percent)

                # Process info
                process = psutil.Process(os.getpid())
                self.add_metric("process_cpu_percent", process.cpu_percent(interval=0.1))
                self.add_metric("process_memory_mb", process.memory_info().rss / (1024 * 1024))

                # Sleep until next interval
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in resource monitoring: {e}")
                time.sleep(interval)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of performance metrics.

        Returns:
            Dictionary with performance summary
        """
        if not self.metrics:
            return {}

        # Group metrics by name
        grouped_metrics = {}
        for metric in self.metrics:
            if metric.name not in grouped_metrics:
                grouped_metrics[metric.name] = []
            grouped_metrics[metric.name].append(metric.value)

        # Calculate statistics for each metric
        summary = {}
        for name, values in grouped_metrics.items():
            summary[name] = {
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "count": len(values)
            }

        # Add runtime
        runtime = time.time() - self.start_time
        summary["runtime_seconds"] = runtime

        return summary


# Create a global performance monitor instance
performance_monitor = PerformanceMonitor()


def measure_time(func):
    """
    Decorator to measure function execution time.

    Args:
        func: Function to decorate

    Returns:
        Decorated function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        execution_time = end_time - start_time
        metric_name = f"func_time_{func.__name__}"
        performance_monitor.add_metric(metric_name, execution_time)

        logger.debug(f"Function {func.__name__} took {execution_time:.4f} seconds")
        return result
    return wrapper


def measure_memory(func):
    """
    Decorator to measure memory usage of a function.

    Args:
        func: Function to decorate

    Returns:
        Decorated function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not PSUTIL_AVAILABLE:
            # If psutil is not available, just run the function
            return func(*args, **kwargs)

        # Get memory usage before
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / (1024 * 1024)  # MB

        # Call the function
        result = func(*args, **kwargs)

        # Get memory usage after
        memory_after = process.memory_info().rss / (1024 * 1024)  # MB
        memory_diff = memory_after - memory_before

        metric_name = f"func_memory_{func.__name__}"
        performance_monitor.add_metric(metric_name, memory_diff)

        logger.debug(f"Function {func.__name__} memory change: {memory_diff:.2f} MB")
        return result
    return wrapper