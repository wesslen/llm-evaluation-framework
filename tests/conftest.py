"""Shared pytest fixtures for the test suite."""

import pytest
import uuid
import os
from datetime import datetime

from src.llm_client import LLMClient
from src.database import get_session, ModelRegistry, UnitTestSuite
from src.config import settings
from src.test_aggregator import TestResultAggregator

# Test Result Aggregation Setup
def pytest_configure(config):
    """Register the test result aggregator at the start of test session."""
    db_url = os.getenv("DATABASE_URL", "sqlite:///database/llm_evaluation.db")
    aggregator = TestResultAggregator(db_url)
    config.pluginmanager.register(aggregator, "result_aggregator")

def pytest_runtest_logreport(report):
    """Record test results as they complete."""
    if report.when == "call":
        aggregator = pytest.config.pluginmanager.get_plugin("result_aggregator")
        
        # Determine test outcome
        outcome = "passed" if report.passed else "failed"
        if hasattr(report, "wasxfail"):
            outcome = "partial"
            
        # Capture error details if test failed
        error_message = None
        if report.failed:
            error_message = str(report.longrepr)
            
        # Add metrics if available in report
        metrics = getattr(report, "test_metrics", {})
        
        aggregator.add_result(
            test_name=report.nodeid,
            outcome=outcome,
            error_message=error_message,
            metrics=metrics
        )

def pytest_sessionfinish(session):
    """Process final results at end of test session."""
    aggregator = session.config.pluginmanager.get_plugin("result_aggregator")
    model_name = os.getenv("MODEL_NAME", "unknown_model")
    metrics, status = aggregator.save_to_database(model_name)

# Environment Fixtures
@pytest.fixture(scope="session")
def model_name():
    """Get the model name from environment."""
    return os.getenv("MODEL_NAME", "unknown_model")

@pytest.fixture(scope="session")
def api_key():
    """Get the API key from environment."""
    return os.getenv("API_KEY")

@pytest.fixture(scope="session")
def api_base_url():
    """Get the API base URL from environment."""
    return os.getenv("API_BASE_URL")

# Database Fixtures
@pytest.fixture(scope="session")
def db_session():
    """Create a database session for testing."""
    session = get_session()
    yield session
    session.close()

@pytest.fixture(scope="session")
def db_url():
    """Get database URL from environment."""
    return os.getenv("DATABASE_URL", "sqlite:///database/llm_evaluation.db")

# LLM Client Fixtures
@pytest.fixture
async def llm_client():
    """Create an LLM client instance."""
    client = LLMClient()
    return client

@pytest.fixture
async def test_model(db_session):
    """Create a test model in the registry."""
    model = ModelRegistry(
        model_id=uuid.uuid4(),
        model_name=settings.llm_model_name,
        model_version="1.0.0",
        provider_type="off_prem_api",
        provider_name="TestProvider",
        model_type="text-generation",
        model_architecture="transformer",
        created_at=datetime.utcnow()
    )
    db_session.add(model)
    db_session.commit()
    return model

# Test Suite Fixtures
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
    
    # Cleanup
    for suite in created_suites:
        db_session.delete(suite)
    db_session.commit()

# Content Fixtures
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

# Cleanup Fixtures
@pytest.fixture(autouse=True)
async def cleanup_db(db_session):
    """Clean up the database after tests."""
    yield
    for table in reversed(ModelRegistry.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()