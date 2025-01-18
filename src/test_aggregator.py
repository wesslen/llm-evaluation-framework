from typing import Dict, List, Any
import json
from datetime import datetime
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

def calculate_model_metrics(test_results: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate overall metrics from test results"""
    total_tests = len(test_results)
    if total_tests == 0:
        return {
            "coverage_rate": 0.0,
            "success_rate": 0.0,
            "partial_success_rate": 0.0
        }

    successful = sum(1 for r in test_results if r.get("outcome") == "passed")
    partial = sum(1 for r in test_results if r.get("outcome") == "partial")
    attempted = sum(1 for r in test_results if r.get("outcome") != "skipped")

    return {
        "coverage_rate": (attempted / total_tests) * 100,
        "success_rate": (successful / total_tests) * 100,
        "partial_success_rate": (partial / total_tests) * 100
    }

def determine_run_status(metrics: Dict[str, float]) -> str:
    """Determine overall run status based on metrics"""
    if metrics["coverage_rate"] >= 80:
        return "success"
    elif metrics["coverage_rate"] >= 50:
        return "partial"
    else:
        return "insufficient_coverage"

class TestResultAggregator:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.current_results = []

    def add_result(self, test_name: str, outcome: str, error_message: str = None, metrics: Dict[str, Any] = None):
        """Record a test result"""
        self.current_results.append({
            "test_name": test_name,
            "outcome": outcome,
            "error_message": error_message,
            "metrics": metrics or {},
            "timestamp": datetime.utcnow().isoformat()
        })

    def save_to_database(self, model_name: str, model_version: str = "latest"):
        """Save results to database and return metrics"""
        metrics = calculate_model_metrics(self.current_results)
        run_status = determine_run_status(metrics)
        
        session = self.Session()
        try:
            # Save results to database using your existing schema
            # This is a simplified example - adjust according to your actual schema
            run_data = {
                "model_name": model_name,
                "model_version": model_version,
                "run_timestamp": datetime.utcnow(),
                "metrics": metrics,
                "status": run_status,
                "results": self.current_results
            }
            
            # Here you would use your actual database models and schema
            # This is just a placeholder for the concept
            print(f"Metrics for {model_name}: {json.dumps(metrics, indent=2)}")
            print(f"Run status: {run_status}")
            
            # Save run_data to your database
            # [Your database save logic here]
            
            session.commit()
            return metrics, run_status
        
        finally:
            session.close()
            self.current_results = []  # Clear results after saving

def pytest_configure(config):
    """Initialize test aggregator at start of test run"""
    db_url = os.getenv("DATABASE_URL", "sqlite:///database/llm_evaluation.db")
    aggregator = TestResultAggregator(db_url)
    config.pluginmanager.register(aggregator, "result_aggregator")

def pytest_runtest_logreport(report):
    """Record test results as they complete"""
    if report.when == "call":  # Only process the test result after it's done
        aggregator = pytest.config.pluginmanager.get_plugin("result_aggregator")
        
        outcome = "passed" if report.passed else "failed"
        if hasattr(report, "wasxfail"):
            outcome = "partial"  # Handle expected failures differently
            
        error_message = None
        if report.failed:
            error_message = str(report.longrepr)
            
        aggregator.add_result(
            test_name=report.nodeid,
            outcome=outcome,
            error_message=error_message
        )

def pytest_sessionfinish(session):
    """Process final results at end of test run"""
    aggregator = session.config.pluginmanager.get_plugin("result_aggregator")
    model_name = os.getenv("MODEL_NAME", "unknown_model")
    metrics, status = aggregator.save_to_database(model_name)
    
    # Write metrics to a file that GitHub Actions can read
    with open("test_metrics.json", "w") as f:
        json.dump({
            "metrics": metrics,
            "status": status,
            "model_name": model_name,
            "timestamp": datetime.utcnow().isoformat()
        }, f, indent=2)