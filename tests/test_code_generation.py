"""Tests for code generation capabilities."""

import pytest
import ast
import json
from typing import List, Dict
import re

from src.llm_client import LLMClient
from src.database import get_session, UnitTestSuite

def extract_code_block(text: str) -> str:
    """Extract code from markdown-style code blocks or plain text."""
    # Try to find Python code blocks
    code_block_match = re.search(r'```(?:python)?\s*(.*?)\s*```', text, re.DOTALL)
    if code_block_match:
        return code_block_match.group(1).strip()
    
    # If no code blocks found, try to extract based on indentation
    lines = text.split('\n')
    code_lines = []
    in_code = False
    
    for line in lines:
        if line.strip().startswith('def ') or line.strip().startswith('class '):
            in_code = True
        if in_code:
            code_lines.append(line)
            
    if code_lines:
        return '\n'.join(code_lines)
        
    # If no clear code blocks found, return the stripped text
    return text.strip()

@pytest.mark.asyncio
async def test_function_implementation(llm_client, db_session):
    """Test implementation of basic functions."""
    client = await llm_client
    
    test_cases = [
        {
            "prompt": """
            Write a Python function called 'fibonacci' that returns the nth number 
            in the Fibonacci sequence. The function should handle inputs n ≥ 1.
            Return the code in a Python code block.
            """,
            "test_inputs": [1, 2, 3, 4, 5, 6],
            "expected_outputs": [1, 1, 2, 3, 5, 8],
            "required_elements": ["def fibonacci", "return"]
        },
        {
            "prompt": """
            Write a Python function called 'is_palindrome' that checks if a string 
            is a palindrome (reads the same forwards and backwards). The function 
            should ignore spaces and be case-insensitive.
            Return the code in a Python code block.
            """,
            "test_inputs": ["radar", "A man a plan a canal Panama", "hello"],
            "expected_outputs": [True, True, False],
            "required_elements": ["def is_palindrome", "return", "lower()"]
        }
    ]
    
    for case in test_cases:
        response = await client.generate(
            prompt=case["prompt"],
            max_tokens=300,
            temperature=0.0
        )
        
        raw_code = response["choices"][0]["text"].strip()
        code = extract_code_block(raw_code)
        
        # Check for required code elements
        for element in case["required_elements"]:
            assert element in code, f"Missing required code element: {element}"
        
        # Validate code is syntactically correct
        try:
            ast.parse(code)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\nCode:\n{code}")

@pytest.mark.asyncio
async def test_algorithm_solutions(llm_client, db_session):
    """Test implementation of common algorithms."""
    client = await llm_client
    
    algorithms = [
        {
            "name": "Binary Search",
            "prompt": """
            Implement a binary search function in Python that finds the index of a 
            target value in a sorted list. Return -1 if the target is not found.
            Return the code in a Python code block.
            """,
            "requirements": [
                "Input validation",
                "Handle empty list",
                "Return correct index",
                "Return -1 if not found"
            ]
        },
        {
            "name": "Merge Sort",
            "prompt": """
            Implement the merge sort algorithm in Python to sort a list of numbers 
            in ascending order. Return the code in a Python code block.
            """,
            "requirements": [
                "Divide and conquer approach",
                "Merge function",
                "Handle empty or single-element lists",
                "Maintain stable sort"
            ]
        }
    ]
    
    for algo in algorithms:
        response = await client.generate(
            prompt=algo["prompt"],
            max_tokens=500,
            temperature=0.0
        )
        
        raw_code = response["choices"][0]["text"].strip()
        code = extract_code_block(raw_code)
        
        # Verify syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            pytest.fail(f"Generated {algo['name']} code has syntax error: {e}\nCode:\n{code}")
        
        # Check for algorithm-specific requirements
        for req in algo["requirements"]:
            assert any(keyword in code.lower() for keyword in req.lower().split()), \
                f"Missing requirement: {req}"

@pytest.mark.asyncio
async def test_code_refactoring(llm_client, db_session):
    """Test code refactoring capabilities."""
    client = await llm_client
    
    original_code = """
    def process_data(data):
        result = []
        for i in range(len(data)):
            if data[i] > 0:
                if data[i] % 2 == 0:
                    if data[i] < 100:
                        result.append(data[i] * 2)
        return result
    """
    
    refactor_prompt = f"""
    Refactor this code to improve readability and efficiency. The code should:
    1. Use list comprehension
    2. Reduce nesting
    3. Add type hints
    4. Add docstring
    
    Return the refactored code in a Python code block.
    
    Original code:
    {original_code}
    """
    
    response = await client.generate(
        prompt=refactor_prompt,
        max_tokens=400,
        temperature=0.0
    )
    
    raw_code = response["choices"][0]["text"].strip()
    refactored_code = extract_code_block(raw_code)
    
    # Verify syntax first
    try:
        ast.parse(refactored_code)
    except SyntaxError as e:
        pytest.fail(f"Generated code has syntax error: {e}\nCode:\n{refactored_code}")
    
    # Check for improvements
    required_elements = [
        "def process_data",
        "List[",  # Type hints
        '"""',    # Docstring
        "[",      # List comprehension
        "return"
    ]
    
    for element in required_elements:
        assert element in refactored_code, f"Missing element in refactored code: {element}"
    
    # Verify the refactored code has less nesting
    original_nesting = original_code.count("    ")
    refactored_nesting = refactored_code.count("    ")
    assert refactored_nesting < original_nesting, "Refactored code should have less nesting"

@pytest.mark.asyncio
async def test_error_handling(llm_client, db_session):
    """Test generation of code with proper error handling."""
    client = await llm_client
    
    prompt = """
    Write a Python function that reads a JSON file and extracts specific fields. 
    The function should handle all possible errors (file not found, invalid JSON, 
    missing fields) gracefully. Return the code in a Python code block.
    """
    
    response = await client.generate(
        prompt=prompt,
        max_tokens=400,
        temperature=0.0
    )
    
    raw_code = response["choices"][0]["text"].strip()
    code = extract_code_block(raw_code)
    
    # Verify syntax first
    try:
        ast.parse(code)
    except SyntaxError as e:
        pytest.fail(f"Generated code has syntax error: {e}\nCode:\n{code}")
    
    # Check for error handling constructs
    required_elements = [
        "try:",
        "except",
        "FileNotFoundError",
        "json.JSONDecodeError",
        "raise"
    ]
    
    for element in required_elements:
        assert element in code, f"Missing error handling element: {element}"