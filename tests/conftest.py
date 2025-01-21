"""Shared pytest fixtures for the test suite."""

import pytest
import uuid
import os
from datetime import datetime
import json

from src.llm_client import LLMClient
from src.database import get_session, ModelRegistry, UnitTestSuite
from src.config import settings

# Global variable to store test results
class TestResults:
    def __init__(self):
        self.results = []
        self.current_test = None

test_results = TestResults()

def pytest_configure(config):
    """Initial test session configuration."""
    test_results.results = []

def pytest_runtest_logreport(report):
    """Process individual test results."""
    if report.when == "call":  # Only process the test result after it's done
        # Determine test outcome
        outcome = "passed" if report.passed else "failed"
        if hasattr(report, "wasxfail"):
            outcome = "partial"
            
        # Create result entry
        result = {
            "test_name": report.nodeid,
            "outcome": outcome,
            "error_message": str(report.longrepr) if report.failed else None,
            "duration": report.duration,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        test_results.results.append(result)

def pytest_sessionfinish(session, exitstatus):
    """Process final results at end of test session."""
    # Calculate metrics
    total_tests = len(test_results.results)
    if total_tests > 0:
        successful = sum(1 for r in test_results.results if r["outcome"] == "passed")
        partial = sum(1 for r in test_results.results if r["outcome"] == "partial")
        attempted = sum(1 for r in test_results.results if r["outcome"] != "skipped")
        
        metrics = {
            "coverage_rate": (attempted / total_tests) * 100,
            "success_rate": (successful / total_tests) * 100,
            "partial_success_rate": (partial / total_tests) * 100
        }
        
        # Determine overall status
        if metrics["coverage_rate"] >= 80:
            status = "success"
        elif metrics["coverage_rate"] >= 50:
            status = "partial"
        else:
            status = "insufficient_coverage"

        # Save metrics to file
        model_name = os.getenv("MODEL_NAME", "unknown_model")
        output = {
            "metrics": metrics,
            "status": status,
            "model_name": model_name,
            "timestamp": datetime.utcnow().isoformat(),
            "results": test_results.results
        }

        with open("test_metrics.json", "w") as f:
            json.dump(output, f, indent=2)

        # Log metrics for visibility
        print(f"Metrics for {model_name}: {json.dumps(metrics, indent=2)}")
        print(f"Run status: {status}")

# Database Fixtures
@pytest.fixture(scope="session")
def db_session():
    """Create a database session for testing."""
    session = get_session()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def llm_client():
    """Create an LLM client instance."""
    return LLMClient()

@pytest.fixture
def test_model(db_session):
    """Create a test model in the registry."""
    model = ModelRegistry(
        model_id=uuid.uuid4(),
        model_name=settings.model_name,
        model_version="1.0.0",
        provider_type="off_prem_api",
        provider_name="TestProvider",
        model_type="text-generation",
        model_architecture="transformer",
        created_at=datetime.utcnow()
    )
    db_session.add(model)
    db_session.commit()
    
    yield model
    
    # Don't clean up the model - we want to keep it in the database

@pytest.fixture
def make_test_suite(db_session):
    """Factory fixture for creating uniquely named test suites."""
    created_suites = []
    
    def _make_suite(name_prefix, description, category, priority=1):
        suite = UnitTestSuite(
            suite_id=uuid.uuid4(),
            suite_name=f"{name_prefix}_{uuid.uuid4().hex[:8]}",
            description=description,
            category=category,
            priority=priority
        )
        db_session.add(suite)
        db_session.commit()
        created_suites.append(suite)
        return suite
    
    yield _make_suite
    
    # Don't clean up test suites - we want to keep them

@pytest.fixture
def sample_texts():
    """Provide sample texts for testing."""
    return {
        "short": "The quick brown fox jumps over the lazy dog.",
        "medium": """
            Machine learning is a subset of artificial intelligence that involves 
            training computer systems to learn from data without explicit programming. 
            This allows systems to improve their performance over time.
        """,
        "long": """
            The James Webb Space Telescope (JWST) is the largest and most powerful 
            space telescope ever built. Launched in December 2021, it uses infrared 
            observation to peer deeper into space than ever before. The telescope's 
            primary mirror consists of 18 hexagonal segments and measures 6.5 meters 
            in diameter. Unlike its predecessor, the Hubble Space Telescope, JWST 
            orbits the Sun at the second Lagrange point (L2), approximately 1.5 
            million kilometers from Earth.
        """
    }

@pytest.fixture
def test_prompts():
    """Provide test prompts for different tasks."""
    return {
        "summarize": "Please summarize the following text concisely:",
        "analyze": "Please analyze the main themes and key points in this text:",
        "extract": "Please extract the key facts from this text in bullet points:",
        "compare": "Please compare and contrast the following two texts:"
    }