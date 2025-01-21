"""Tests for logical reasoning capabilities."""

import pytest
import uuid

from src.llm_client import LLMClient
from src.database import get_session, UnitTestSuite, UnitTest

@pytest.mark.asyncio
async def test_logical_deduction(llm_client, db_session, make_test_suite):
    """Test logical deduction capabilities."""
    client = llm_client  # Removed await
    
    suite = make_test_suite(
        name_prefix="logical_deduction",
        description="Tests for logical deduction",
        category="reasoning"
    )
    
    premises = """
    1. All programmers like coffee
    2. Some coffee drinkers work at night
    3. Alice is a programmer
    """
    
    questions = [
        {
            "query": "Does Alice like coffee?",
            "expected_keywords": ["yes", "true", "likes", "does"]
        },
        {
            "query": "Do all programmers work at night?",
            "expected_keywords": ["cannot", "unknown", "insufficient", "maybe"]
        }
    ]
    
    for i, question in enumerate(questions):
        test = UnitTest(
            test_id=uuid.uuid4(),
            suite_id=suite.suite_id,
            test_name=f"Deduction Test {i+1}",
            test_type="logical_deduction",
            input_data={
                "premises": premises,
                "question": question["query"]
            },
            expected_output={"keywords": question["expected_keywords"]}
        )
        db_session.add(test)
    db_session.commit()
    
    for question in questions:
        prompt = f"""
        Given these premises:
        {premises}
        
        Question: {question["query"]}
        Provide a direct answer without explanation.
        """
        
        response = await client.generate(
            prompt=prompt,
            max_tokens=50,
            temperature=0.0
        )
        
        answer = response["choices"][0]["text"].strip().lower()
        assert any(keyword in answer for keyword in question["expected_keywords"]), \
            f"Answer '{answer}' does not contain any expected keywords: {question['expected_keywords']}"

@pytest.mark.asyncio
async def test_cause_effect_analysis(llm_client, db_session, make_test_suite):
    """Test cause and effect analysis."""
    client = llm_client  # Removed await
    
    suite = make_test_suite(
        name_prefix="cause_effect",
        description="Tests for cause and effect analysis",
        category="reasoning"
    )
    
    scenarios = [
        {
            "scenario": """
            In a city, the following events occurred:
            1. A major employer relocated to the city
            2. Housing prices increased by 25%
            3. Traffic congestion worsened
            4. Local businesses reported higher sales
            """,
            "query": "What was the likely initial cause of these changes?",
            "expected_phrase": "employer", 
        }
    ]
    
    for i, scenario in enumerate(scenarios):
        test = UnitTest(
            test_id=uuid.uuid4(),
            suite_id=suite.suite_id,
            test_name=f"Cause Effect Test {i+1}",
            test_type="cause_effect",
            input_data={
                "scenario": scenario["scenario"],
                "question": scenario["query"]
            },
            expected_output={"key_phrase": scenario["expected_phrase"]}
        )
        db_session.add(test)
    db_session.commit()
    
    for scenario in scenarios:
        prompt = f"""
        {scenario['scenario']}
        
        {scenario['query']}
        Answer briefly in one line.
        """
        
        response = await client.generate(
            prompt=prompt,
            max_tokens=50,
            temperature=0.0
        )
        
        answer = response["choices"][0]["text"].strip().lower()
        assert scenario["expected_phrase"] in answer, \
            f"Expected to find '{scenario['expected_phrase']}' in answer: {answer}"

@pytest.mark.asyncio
async def test_analogical_reasoning(llm_client, db_session, make_test_suite):
    """Test analogical reasoning capabilities."""
    client = llm_client  # Removed await
    
    suite = make_test_suite(
        name_prefix="analogical",
        description="Tests for analogical reasoning",
        category="reasoning"
    )
    
    analogies = [
        {
            "prompt": "Teacher is to Student as Doctor is to:",
            "expected": "patient",
            "incorrect": ["nurse", "medicine", "hospital"]
        }
    ]
    
    for i, analogy in enumerate(analogies):
        test = UnitTest(
            test_id=uuid.uuid4(),
            suite_id=suite.suite_id,
            test_name=f"Analogy Test {i+1}",
            test_type="analogy",
            input_data={"prompt": analogy["prompt"]},
            expected_output={
                "answer": analogy["expected"],
                "incorrect": analogy["incorrect"]
            }
        )
        db_session.add(test)
    db_session.commit()
    
    for analogy in analogies:
        response = await client.generate(
            prompt=f"{analogy['prompt']} Provide just the one-word answer.",
            max_tokens=50,
            temperature=0.0
        )
        
        answer = response["choices"][0]["text"].strip().lower()
        assert answer == analogy["expected"], \
            f"Expected {analogy['expected']} but got {answer}"