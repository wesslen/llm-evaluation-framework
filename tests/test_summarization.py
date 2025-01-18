"""Tests for text summarization capabilities."""

import pytest
import uuid
from datetime import datetime

from src.llm_client import LLMClient
from src.database import get_session, ModelRegistry, UnitTestSuite, UnitTest

@pytest.mark.asyncio
async def test_article_summarization(llm_client, db_session, make_test_suite):
    """Test article summarization capabilities."""
    # Need to await our async fixture
    client = await llm_client
    
    # Create a uniquely named test suite
    suite = make_test_suite(
        name_prefix="summarization",
        description="Tests for text summarization capabilities",
        category="summarization"
    )
    
    # Test article
    article = """
    The James Webb Space Telescope has revolutionized our view of the cosmos.
    Launched in December 2021, this $10 billion observatory has provided
    unprecedented views of distant galaxies, star-forming regions, and
    exoplanets. Its infrared capabilities allow it to peer through cosmic
    dust and see light from the earliest galaxies in the universe.
    """
    
    # Define expected key points
    key_points = [
        "James Webb Space Telescope",
        "launched December 2021",
        "infrared observation",
        "galaxies and exoplanets"
    ]
    
    # Create test case in database
    test_case = UnitTest(
        test_id=uuid.uuid4(),
        suite_id=suite.suite_id,
        test_name="Article Summarization",
        test_type="summarization",
        test_description="Test summarization of a scientific article",
        input_data={"article": article},
        expected_output={"key_points": key_points}
    )
    db_session.add(test_case)
    db_session.commit()
    
    # Get summary from model
    response = await client.generate(
        prompt=f"Please summarize this article concisely: {article}",
        max_tokens=100,
        temperature=0.3
    )
    
    summary = response["choices"][0]["text"].strip()
    
    # Check if key points are present
    for point in key_points:
        assert point.lower() in summary.lower(), f"Missing key point: {point}"
    
    # Record test results
    metrics = await client.analyze_response(response)
    
    assert metrics["finish_reason"] == "stop", "Generation did not complete normally"
    assert metrics["tokens_generated"] <= 100, "Generated text exceeds token limit"

@pytest.mark.asyncio
async def test_multi_document_summarization():
    """Test summarization of multiple documents."""
    pass

@pytest.mark.asyncio
async def test_bullet_point_extraction():
    """Test extraction of key points in bullet format."""
    pass