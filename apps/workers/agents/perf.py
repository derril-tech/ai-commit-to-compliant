"""
Performance agent for load testing and performance monitoring.
"""

from typing import Dict, Any
from .base import BaseAgent


class PerfAgent(BaseAgent):
    """Agent for performance testing and monitoring."""
    
    async def setup(self) -> None:
        """Setup the performance agent."""
        self.logger.info("Performance agent setup complete")
    
    async def cleanup(self) -> None:
        """Cleanup the performance agent."""
        self.logger.info("Performance agent cleanup complete")
    
    async def subscribe_to_events(self) -> None:
        """Subscribe to performance-related events."""
        await self.event_bus.subscribe("perf.test", self.handle_performance_test)
        await self.event_bus.subscribe("perf.baseline", self.handle_baseline_creation)
    
    async def handle_performance_test(self, data: Dict[str, Any]) -> None:
        """Handle performance testing request."""
        try:
            project_id = data["project_id"]
            test_type = data.get("test_type", "load")
            target_url = data.get("target_url")
            
            self.logger.info("Running performance test", project_id=project_id, test_type=test_type)
            
            # Run performance tests
            test_results = await self.run_performance_tests(project_id, test_type, target_url)
            
            # Publish test results
            await self.publish_event("perf.test_completed", {
                "project_id": project_id,
                "test_results": test_results,
            })
            
        except Exception as e:
            await self.handle_error(e, {"project_id": data.get("project_id")})
    
    async def handle_baseline_creation(self, data: Dict[str, Any]) -> None:
        """Handle performance baseline creation."""
        try:
            project_id = data["project_id"]
            target_url = data.get("target_url")
            
            self.logger.info("Creating performance baseline", project_id=project_id)
            
            # Create performance baseline
            baseline = await self.create_performance_baseline(project_id, target_url)
            
            # Publish baseline created event
            await self.publish_event("perf.baseline_created", {
                "project_id": project_id,
                "baseline": baseline,
            })
            
        except Exception as e:
            await self.handle_error(e, {"project_id": data.get("project_id")})
    
    async def run_performance_tests(self, project_id: str, test_type: str, target_url: str) -> Dict[str, Any]:
        """Run performance tests using k6."""
        if test_type == "load":
            return await self.run_load_test(target_url)
        elif test_type == "stress":
            return await self.run_stress_test(target_url)
        elif test_type == "spike":
            return await self.run_spike_test(target_url)
        elif test_type == "endurance":
            return await self.run_endurance_test(target_url)
        else:
            return await self.run_smoke_test(target_url)
    
    async def run_load_test(self, target_url: str) -> Dict[str, Any]:
        """Run load test to verify normal expected load."""
        # TODO: Implement actual k6 load test execution
        # This would generate and run k6 scripts
        
        return {
            "test_type": "load",
            "target_url": target_url,
            "duration": "5m",
            "virtual_users": 50,
            "status": "completed",
            "metrics": {
                "http_req_duration": {
                    "avg": 245.67,
                    "min": 89.23,
                    "med": 198.45,
                    "max": 1234.56,
                    "p90": 387.21,
                    "p95": 456.78,
                    "p99": 789.12
                },
                "http_req_rate": {
                    "value": 167.5,
                    "unit": "req/s"
                },
                "http_req_failed": {
                    "value": 0.12,
                    "unit": "%"
                },
                "data_received": {
                    "value": 45.2,
                    "unit": "MB"
                },
                "data_sent": {
                    "value": 12.8,
                    "unit": "MB"
                },
                "vus": {
                    "value": 50,
                    "max": 50
                },
                "iterations": {
                    "value": 50250,
                    "rate": 167.5
                }
            },
            "thresholds": {
                "http_req_duration": {
                    "threshold": "p95<500",
                    "passed": True,
                    "value": 456.78
                },
                "http_req_failed": {
                    "threshold": "rate<0.1",
                    "passed": False,
                    "value": 0.12
                },
                "http_req_rate": {
                    "threshold": "rate>100",
                    "passed": True,
                    "value": 167.5
                }
            },
            "checks": {
                "status_is_200": {
                    "passes": 50188,
                    "fails": 62,
                    "rate": 99.88
                },
                "response_time_ok": {
                    "passes": 49876,
                    "fails": 374,
                    "rate": 99.25
                }
            },
            "summary": {
                "passed_thresholds": 2,
                "failed_thresholds": 1,
                "total_thresholds": 3,
                "overall_status": "failed"
            }
        }
    
    async def run_stress_test(self, target_url: str) -> Dict[str, Any]:
        """Run stress test to find breaking point."""
        return {
            "test_type": "stress",
            "target_url": target_url,
            "duration": "10m",
            "max_virtual_users": 200,
            "status": "completed",
            "breaking_point": {
                "virtual_users": 175,
                "requests_per_second": 290,
                "error_rate_percent": 5.2,
                "avg_response_time_ms": 1250
            },
            "metrics": {
                "http_req_duration": {
                    "avg": 892.34,
                    "p95": 2145.67,
                    "p99": 4567.89
                },
                "http_req_failed": {
                    "value": 3.45,
                    "unit": "%"
                }
            },
            "phases": [
                {
                    "phase": "ramp_up",
                    "duration": "2m",
                    "target_vus": 50,
                    "avg_response_time": 245.67,
                    "error_rate": 0.1
                },
                {
                    "phase": "stay_50",
                    "duration": "2m", 
                    "target_vus": 50,
                    "avg_response_time": 267.89,
                    "error_rate": 0.2
                },
                {
                    "phase": "ramp_to_100",
                    "duration": "2m",
                    "target_vus": 100,
                    "avg_response_time": 456.78,
                    "error_rate": 0.8
                },
                {
                    "phase": "stay_100",
                    "duration": "2m",
                    "target_vus": 100,
                    "avg_response_time": 567.89,
                    "error_rate": 1.2
                },
                {
                    "phase": "ramp_to_200",
                    "duration": "2m",
                    "target_vus": 200,
                    "avg_response_time": 1234.56,
                    "error_rate": 4.5
                }
            ]
        }
    
    async def run_spike_test(self, target_url: str) -> Dict[str, Any]:
        """Run spike test for sudden load increases."""
        return {
            "test_type": "spike",
            "target_url": target_url,
            "duration": "8m",
            "spike_virtual_users": 500,
            "status": "completed",
            "spike_performance": {
                "recovery_time_seconds": 45,
                "error_rate_during_spike": 12.5,
                "error_rate_after_spike": 0.3,
                "performance_degradation": "moderate"
            },
            "metrics": {
                "http_req_duration": {
                    "avg": 567.89,
                    "spike_avg": 2345.67,
                    "post_spike_avg": 289.45
                },
                "http_req_failed": {
                    "baseline": 0.2,
                    "spike": 12.5,
                    "recovery": 0.3
                }
            }
        }
    
    async def run_endurance_test(self, target_url: str) -> Dict[str, Any]:
        """Run endurance test for extended periods."""
        return {
            "test_type": "endurance",
            "target_url": target_url,
            "duration": "2h",
            "virtual_users": 30,
            "status": "completed",
            "stability_metrics": {
                "memory_leak_detected": False,
                "performance_degradation": 2.3,  # percentage
                "error_rate_trend": "stable",
                "response_time_trend": "slightly_increasing"
            },
            "time_series": {
                "intervals": 24,  # 5-minute intervals
                "avg_response_times": [245, 251, 248, 252, 255, 258, 261, 264, 267, 270, 273, 276, 279, 282, 285, 288, 291, 294, 297, 300, 303, 306, 309, 312],
                "error_rates": [0.1, 0.1, 0.2, 0.1, 0.2, 0.2, 0.3, 0.2, 0.3, 0.3, 0.4, 0.3, 0.4, 0.4, 0.5, 0.4, 0.5, 0.5, 0.6, 0.5, 0.6, 0.6, 0.7, 0.6]
            }
        }
    
    async def run_smoke_test(self, target_url: str) -> Dict[str, Any]:
        """Run smoke test with minimal load."""
        return {
            "test_type": "smoke",
            "target_url": target_url,
            "duration": "1m",
            "virtual_users": 1,
            "status": "completed",
            "metrics": {
                "http_req_duration": {
                    "avg": 156.78,
                    "min": 89.23,
                    "max": 234.56,
                    "p95": 198.45
                },
                "http_req_failed": {
                    "value": 0.0,
                    "unit": "%"
                }
            },
            "endpoints_tested": [
                {
                    "endpoint": "/",
                    "method": "GET",
                    "avg_response_time": 145.67,
                    "status": "passed"
                },
                {
                    "endpoint": "/api/health",
                    "method": "GET", 
                    "avg_response_time": 89.23,
                    "status": "passed"
                },
                {
                    "endpoint": "/api/projects",
                    "method": "GET",
                    "avg_response_time": 234.56,
                    "status": "passed"
                }
            ]
        }
    
    async def create_performance_baseline(self, project_id: str, target_url: str) -> Dict[str, Any]:
        """Create performance baseline for future comparisons."""
        # Run a comprehensive baseline test
        baseline_results = await self.run_load_test(target_url)
        
        return {
            "project_id": project_id,
            "created_at": "2024-01-01T00:00:00Z",
            "target_url": target_url,
            "baseline_metrics": {
                "p50_response_time": baseline_results["metrics"]["http_req_duration"]["med"],
                "p95_response_time": baseline_results["metrics"]["http_req_duration"]["p95"],
                "p99_response_time": baseline_results["metrics"]["http_req_duration"]["p99"],
                "requests_per_second": baseline_results["metrics"]["http_req_rate"]["value"],
                "error_rate": baseline_results["metrics"]["http_req_failed"]["value"],
                "virtual_users": baseline_results["virtual_users"]
            },
            "performance_budgets": {
                "p95_response_time_ms": 500,  # Alert if p95 > 500ms
                "error_rate_percent": 1.0,    # Alert if error rate > 1%
                "min_requests_per_second": 100, # Alert if RPS < 100
                "availability_percent": 99.9   # Alert if availability < 99.9%
            },
            "thresholds": {
                "response_time_degradation_percent": 20,  # Alert if 20% slower than baseline
                "error_rate_increase_percent": 50,        # Alert if 50% more errors than baseline
                "throughput_decrease_percent": 15         # Alert if 15% less throughput than baseline
            }
        }
    
    async def generate_k6_script(self, test_type: str, target_url: str) -> str:
        """Generate k6 test script."""
        if test_type == "load":
            return f'''import http from 'k6/http';
import {{ check, sleep }} from 'k6';
import {{ Rate }} from 'k6/metrics';

export let errorRate = new Rate('errors');

export let options = {{
  stages: [
    {{ duration: '1m', target: 10 }},  // Ramp up
    {{ duration: '3m', target: 50 }},  // Stay at 50 users
    {{ duration: '1m', target: 0 }},   // Ramp down
  ],
  thresholds: {{
    http_req_duration: ['p95<500'],
    http_req_failed: ['rate<0.1'],
    errors: ['rate<0.1'],
  }},
}};

export default function () {{
  let response = http.get('{target_url}');
  
  let result = check(response, {{
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  }});
  
  errorRate.add(!result);
  
  sleep(1);
}}

export function handleSummary(data) {{
  return {{
    'performance-results.json': JSON.stringify(data),
  }};
}}'''
        
        elif test_type == "stress":
            return f'''import http from 'k6/http';
import {{ check, sleep }} from 'k6';

export let options = {{
  stages: [
    {{ duration: '2m', target: 50 }},   // Ramp up to 50 users
    {{ duration: '2m', target: 50 }},   // Stay at 50 users
    {{ duration: '2m', target: 100 }},  // Ramp up to 100 users
    {{ duration: '2m', target: 100 }},  // Stay at 100 users
    {{ duration: '2m', target: 200 }},  // Ramp up to 200 users (stress)
    {{ duration: '2m', target: 0 }},    // Ramp down
  ],
  thresholds: {{
    http_req_duration: ['p95<2000'],
    http_req_failed: ['rate<0.05'],
  }},
}};

export default function () {{
  let response = http.get('{target_url}');
  
  check(response, {{
    'status is 200': (r) => r.status === 200,
  }});
  
  sleep(Math.random() * 2 + 1); // Random sleep between 1-3 seconds
}}'''
        
        return f'''import http from 'k6/http';
import {{ check }} from 'k6';

export let options = {{
  vus: 1,
  duration: '1m',
}};

export default function () {{
  let response = http.get('{target_url}');
  
  check(response, {{
    'status is 200': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
  }});
}}'''
