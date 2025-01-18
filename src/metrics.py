"""Metrics collection and analysis for LLM evaluation."""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import statistics
from dataclasses import dataclass

@dataclass
class ResponseMetrics:
    """Container for response-level metrics."""
    
    response_time: float  # in milliseconds
    token_count: int
    completion_status: str
    error_type: Optional[str] = None

@dataclass
class QualityMetrics:
    """Container for quality-related metrics."""
    
    relevance_score: float  # 0-1
    coherence_score: float  # 0-1
    factual_accuracy: float  # 0-1
    grammar_score: float  # 0-1

class MetricsCollector:
    """Collect and analyze metrics from model responses."""
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.responses: List[ResponseMetrics] = []
        self.quality_scores: List[QualityMetrics] = []
        
    def add_response_metrics(self, metrics: ResponseMetrics):
        """Add response metrics to the collection."""
        self.responses.append(metrics)
        
    def add_quality_metrics(self, metrics: QualityMetrics):
        """Add quality metrics to the collection."""
        self.quality_scores.append(metrics)
        
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Calculate summary statistics for collected metrics."""
        if not self.responses:
            return {}
            
        response_times = [r.response_time for r in self.responses]
        token_counts = [r.token_count for r in self.responses]
        
        stats = {
            "response_time": {
                "mean": statistics.mean(response_times),
                "median": statistics.median(response_times),
                "p95": statistics.quantiles(response_times, n=20)[18],
                "min": min(response_times),
                "max": max(response_times)
            },
            "token_count": {
                "mean": statistics.mean(token_counts),
                "median": statistics.median(token_counts),
                "min": min(token_counts),
                "max": max(token_counts)
            },
            "completion_rate": self._calculate_completion_rate(),
            "error_rate": self._calculate_error_rate()
        }
        
        if self.quality_scores:
            stats["quality"] = self._calculate_quality_metrics()
            
        return stats
        
    def _calculate_completion_rate(self) -> float:
        """Calculate the rate of successful completions."""
        if not self.responses:
            return 0.0
        successful = sum(1 for r in self.responses if r.completion_status == "stop")
        return successful / len(self.responses)
        
    def _calculate_error_rate(self) -> float:
        """Calculate the rate of errors."""
        if not self.responses:
            return 0.0
        errors = sum(1 for r in self.responses if r.error_type is not None)
        return errors / len(self.responses)
        
    def _calculate_quality_metrics(self) -> Dict[str, float]:
        """Calculate average quality metrics."""
        return {
            "relevance": statistics.mean(q.relevance_score for q in self.quality_scores),
            "coherence": statistics.mean(q.coherence_score for q in self.quality_scores),
            "factual_accuracy": statistics.mean(q.factual_accuracy for q in self.quality_scores),
            "grammar": statistics.mean(q.grammar_score for q in self.quality_scores)
        }
        
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in the specified format."""
        stats = self.get_summary_statistics()
        if format == "json":
            return json.dumps(stats, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")

class PerformanceMonitor:
    """Monitor and track model performance over time."""
    
    def __init__(self, window_size: timedelta = timedelta(hours=1)):
        """Initialize the performance monitor."""
        self.window_size = window_size
        self.metrics: List[Dict[str, Any]] = []
        
    def add_metric(self, metric: Dict[str, Any]):
        """Add a metric data point with timestamp."""
        metric["timestamp"] = datetime.utcnow()
        self.metrics.append(metric)
        self._prune_old_metrics()
        
    def _prune_old_metrics(self):
        """Remove metrics outside the window size."""
        cutoff = datetime.utcnow() - self.window_size
        self.metrics = [m for m in self.metrics if m["timestamp"] > cutoff]
        
    def get_current_stats(self) -> Dict[str, Any]:
        """Get statistics for the current window."""
        if not self.metrics:
            return {}
            
        return {
            "window_start": min(m["timestamp"] for m in self.metrics),
            "window_end": max(m["timestamp"] for m in self.metrics),
            "sample_count": len(self.metrics),
            "metrics": self._calculate_window_stats()
        }
        
    def _calculate_window_stats(self) -> Dict[str, Any]:
        """Calculate statistics for metrics in the current window."""
        # Implementation depends on specific metrics being tracked
        return {}