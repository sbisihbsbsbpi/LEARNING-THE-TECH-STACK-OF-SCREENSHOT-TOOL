"""
Performance Metrics Configuration
Single source of truth for all performance-related constants
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class PerformanceMetrics:
    """Performance metrics for screenshot tool"""
    
    # ===== Batch Configuration =====
    batch_1_urls: int = 18
    batch_2_urls: int = 19
    batch_3_urls: int = 16
    
    # ===== Timing (seconds) =====
    batch_timeout: float = 120  # Real Browser Mode timeout
    ui_load_wait_min: float = 10.0
    ui_load_wait_max: float = 12.0
    
    # ===== Calculated Properties =====
    @property
    def total_urls(self) -> int:
        """Total number of URLs across all batches"""
        return self.batch_1_urls + self.batch_2_urls + self.batch_3_urls
    
    @property
    def total_time(self) -> float:
        """Total time for all batches (seconds)"""
        return self.batch_timeout * 3  # 3 batches
    
    @property
    def total_time_minutes(self) -> float:
        """Total time in minutes"""
        return self.total_time / 60
    
    @property
    def avg_time_per_url(self) -> float:
        """Average time per URL (seconds)"""
        return self.total_time / self.total_urls
    
    @property
    def sequential_time(self) -> float:
        """Time if processed sequentially (seconds)"""
        return self.total_urls * self.ui_load_wait_max
    
    @property
    def sequential_time_minutes(self) -> float:
        """Sequential time in minutes"""
        return self.sequential_time / 60
    
    @property
    def speedup(self) -> float:
        """Speedup factor vs sequential"""
        return self.sequential_time / self.total_time
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for template rendering"""
        return {
            # Batch config
            'batch_1_urls': self.batch_1_urls,
            'batch_2_urls': self.batch_2_urls,
            'batch_3_urls': self.batch_3_urls,
            'total_urls': self.total_urls,
            
            # Timing
            'batch_timeout': self.batch_timeout,
            'ui_load_wait_min': self.ui_load_wait_min,
            'ui_load_wait_max': self.ui_load_wait_max,
            
            # Calculated
            'total_time': self.total_time,
            'total_time_minutes': self.total_time_minutes,
            'avg_time_per_url': self.avg_time_per_url,
            'sequential_time': self.sequential_time,
            'sequential_time_minutes': self.sequential_time_minutes,
            'speedup': self.speedup,
        }


# Global instance
metrics = PerformanceMetrics()


if __name__ == "__main__":
    # Print metrics for verification
    print("Performance Metrics:")
    print(f"  Total URLs: {metrics.total_urls}")
    print(f"  Batch timeout: {metrics.batch_timeout}s")
    print(f"  Total time: {metrics.total_time}s ({metrics.total_time_minutes:.1f} min)")
    print(f"  Avg per URL: {metrics.avg_time_per_url:.1f}s")
    print(f"  Sequential: {metrics.sequential_time}s ({metrics.sequential_time_minutes:.1f} min)")
    print(f"  Speedup: {metrics.speedup:.1f}x")

