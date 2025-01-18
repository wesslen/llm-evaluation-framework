"""Tests for mathematical capabilities."""

import pytest
import ast
import uuid

from src.llm_client import LLMClient
from src.database import get_session, UnitTestSuite, UnitTest

@pytest.mark.asyncio
async def test_arithmetic_operations(llm_client, db_session, make_test_suite):
    """Test basic arithmetic operations."""
    client = await llm_client
    
    suite = make_test_suite(
        name_prefix="arithmetic",
        description="Tests for basic arithmetic operations",
        category="mathematics"
    )
    
    test_cases = [
        {
            "prompt": "What is the result of multiplying 23.5 by 8.75?",
            "expected": 205.625
        },
        {
            "prompt": "What is 1234 divided by 56.5?",
            "expected": 21.84070796460177
        }
    ]
    
    for i, case in enumerate(test_cases):
        test = UnitTest(
            test_id=uuid.uuid4(),
            suite_id=suite.suite_id,
            test_name=f"Arithmetic Test {i+1}",
            test_type="arithmetic",
            input_data={"prompt": case["prompt"]},
            expected_output={"result": case["expected"]}
        )
        db_session.add(test)
    db_session.commit()
        
    for case in test_cases:
        response = await client.generate(
            prompt=f"{case['prompt']} Provide only the numerical answer without any explanation.",
            max_tokens=50,
            temperature=0.0
        )
        
        result = float(response["choices"][0]["text"].strip().split()[0])
        assert abs(result - case["expected"]) < 0.01, \
            f"Expected {case['expected']} but got {result}"

@pytest.mark.asyncio
async def test_word_problems(llm_client, db_session, make_test_suite):
    """Test solving mathematical word problems."""
    client = await llm_client
    suite = make_test_suite(
        name_prefix="word_problems",
        description="Tests for mathematical word problems",
        category="mathematics"
    )
    
    problems = [
        {
            "prompt": """
            A store sells notebooks for $4.50 each. If a customer buys 12 notebooks
            and has a 20% discount coupon, how much do they pay in total?
            """,
            "expected": 43.20
        }
    ]
    
    for i, problem in enumerate(problems):
        test = UnitTest(
            test_id=uuid.uuid4(),
            suite_id=suite.suite_id,
            test_name=f"Word Problem {i+1}",
            test_type="word_problem",
            input_data={"prompt": problem["prompt"]},
            expected_output={"result": problem["expected"]}
        )
        db_session.add(test)
    db_session.commit()
    
    for problem in problems:
        response = await client.generate(
            prompt=f"{problem['prompt']} Provide only the numerical answer in dollars without any explanation.",
            max_tokens=50,
            temperature=0.0
        )
        
        result = float(response["choices"][0]["text"].strip().split()[0])
        assert abs(result - problem["expected"]) < 0.01, \
            f"Expected ${problem['expected']} but got ${result}"

@pytest.mark.asyncio
async def test_basic_algebra(llm_client, db_session, make_test_suite):
    """Test basic algebraic equation solving."""
    client = await llm_client
    suite = make_test_suite(
        name_prefix="algebra",
        description="Tests for basic algebra",
        category="mathematics"
    )
    
    equations = [
        {
            "prompt": "Solve for x: 3x + 7 = 22",
            "expected": 5
        },
        {
            "prompt": "Solve for x: 2x² + 5x = 12",
            "expected": [1.5, -4]  # Both solutions
        }
    ]
    
    for i, eq in enumerate(equations):
        test = UnitTest(
            test_id=uuid.uuid4(),
            suite_id=suite.suite_id,
            test_name=f"Algebra Test {i+1}",
            test_type="algebra",
            input_data={"prompt": eq["prompt"]},
            expected_output={"result": eq["expected"]}
        )
        db_session.add(test)
    db_session.commit()
    
    # Test first equation (single solution)
    response = await client.generate(
        prompt=f"{equations[0]['prompt']} Provide only the numerical answer without any explanation.",
        max_tokens=50,
        temperature=0.0
    )
    
    result = float(response["choices"][0]["text"].strip().split()[0])
    assert abs(result - equations[0]["expected"]) < 0.01, \
        f"Expected {equations[0]['expected']} but got {result}"

@pytest.mark.asyncio
async def test_mathematical_reasoning(llm_client, db_session, make_test_suite):
    """Test mathematical reasoning and logic."""
    client = await llm_client
    suite = make_test_suite(
        name_prefix="math_reasoning",
        description="Tests for mathematical reasoning",
        category="mathematics"
    )
    
    problems = [
        {
            "prompt": """
            If the sequence follows the pattern: 2, 6, 12, 20, 30, ...
            What will be the next number?
            """,
            "expected": 42
        }
    ]
    
    for i, problem in enumerate(problems):
        test = UnitTest(
            test_id=uuid.uuid4(),
            suite_id=suite.suite_id,
            test_name=f"Reasoning Test {i+1}",
            test_type="reasoning",
            input_data={"prompt": problem["prompt"]},
            expected_output={"result": problem["expected"]}
        )
        db_session.add(test)
    db_session.commit()
    
    for problem in problems:
        response = await client.generate(
            prompt=f"{problem['prompt']} Provide only the numerical answer without any explanation.",
            max_tokens=50,
            temperature=0.0
        )
        
        result = int(response["choices"][0]["text"].strip().split()[0])
        assert result == problem["expected"], \
            f"Expected {problem['expected']} but got {result}"