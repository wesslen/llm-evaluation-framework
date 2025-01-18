"""Tests for few-shot learning capabilities."""

import pytest
import json
from typing import List, Dict, Any

from src.llm_client import LLMClient
from src.database import get_session, UnitTestSuite

@pytest.mark.asyncio
async def test_sentiment_analysis(llm_client, db_session):
    """Test sentiment analysis with few-shot examples."""
    client = await llm_client
    
    examples = [
        {"text": "This product exceeded my expectations!", "sentiment": "positive"},
        {"text": "I regret buying this, complete waste of money.", "sentiment": "negative"},
        {"text": "It works as advertised, nothing special.", "sentiment": "neutral"}
    ]
    
    test_cases = [
        {
            "text": "While it has some flaws, I'm generally satisfied with my purchase.",
            "expected": "positive"
        },
        {
            "text": "Don't bother with this one, seriously disappointed.",
            "expected": "negative"
        },
        {
            "text": "Does what it says on the tin.",
            "expected": "neutral"
        }
    ]
    
    # Create few-shot prompt
    few_shot_prompt = "Classify the sentiment of the following text as positive, negative, or neutral:\n\n"
    for example in examples:
        few_shot_prompt += f"Text: {example['text']}\nSentiment: {example['sentiment']}\n\n"
    
    for case in test_cases:
        prompt = few_shot_prompt + f"Text: {case['text']}\nSentiment:"
        
        response = await client.generate(
            prompt=prompt,
            max_tokens=50,
            temperature=0.3
        )
        
        prediction = response["choices"][0]["text"].strip().lower()
        assert case["expected"] in prediction, f"Expected {case['expected']} but got {prediction}"

@pytest.mark.asyncio
async def test_topic_classification(llm_client, db_session):
    """Test topic classification with few-shot examples."""
    client = await llm_client
    
    examples = [
        {
            "text": "Scientists discover new exoplanet in nearby solar system",
            "topic": "science"
        },
        {
            "text": "Local team wins championship in dramatic final",
            "topic": "sports"
        },
        {
            "text": "New smartphone features revolutionary camera technology",
            "topic": "technology"
        }
    ]
    
    test_articles = [
        {
            "text": "Researchers develop breakthrough in quantum computing",
            "expected": "technology"
        },
        {
            "text": "Study reveals new insights into black hole formation",
            "expected": "science"
        },
        {
            "text": "Player breaks record for most goals in a season",
            "expected": "sports"
        }
    ]
    
    # Create few-shot prompt
    few_shot_prompt = "Classify the topic of the following text as science, sports, or technology:\n\n"
    for example in examples:
        few_shot_prompt += f"Text: {example['text']}\nTopic: {example['topic']}\n\n"
    
    for article in test_articles:
        prompt = few_shot_prompt + f"Text: {article['text']}\nTopic:"
        
        response = await client.generate(
            prompt=prompt,
            max_tokens=50,
            temperature=0.3
        )
        
        prediction = response["choices"][0]["text"].strip().lower()
        assert article["expected"] in prediction, \
            f"Expected {article['expected']} but got {prediction}"

@pytest.mark.asyncio
async def test_intent_classification(llm_client, db_session):
    """Test user intent classification with few-shot examples."""
    client = await llm_client
    
    examples = [
        {
            "text": "What's the current status of my order?",
            "intent": "check_status"
        },
        {
            "text": "I need to return this product",
            "intent": "return_request"
        },
        {
            "text": "Do you ship to international locations?",
            "intent": "shipping_inquiry"
        }
    ]
    
    test_queries = [
        {
            "text": "When will my package arrive?",
            "expected": "check_status"
        },
        {
            "text": "How do I send this item back?",
            "expected": "return_request"
        },
        {
            "text": "Can you deliver to Canada?",
            "expected": "shipping_inquiry"
        }
    ]
    
    # Create few-shot prompt
    few_shot_prompt = "Classify the user intent as check_status, return_request, or shipping_inquiry:\n\n"
    for example in examples:
        few_shot_prompt += f"Query: {example['text']}\nIntent: {example['intent']}\n\n"
    
    for query in test_queries:
        prompt = few_shot_prompt + f"Query: {query['text']}\nIntent:"
        
        response = await client.generate(
            prompt=prompt,
            max_tokens=50,
            temperature=0.3
        )
        
        prediction = response["choices"][0]["text"].strip().lower()
        assert query["expected"] in prediction, \
            f"Expected {query['expected']} but got {prediction}"

@pytest.mark.asyncio
async def test_entity_extraction(llm_client, db_session):
    """Test named entity extraction with few-shot examples."""
    client = await llm_client
    
    examples = [
        {
            "text": "John Smith works at Apple Inc. in California",
            "entities": {
                "person": "John Smith",
                "organization": "Apple Inc.",
                "location": "California"
            }
        },
        {
            "text": "Microsoft CEO Satya Nadella visited London",
            "entities": {
                "person": "Satya Nadella",
                "organization": "Microsoft",
                "location": "London"
            }
        }
    ]
    
    test_cases = [
        {
            "text": "Amazon founder Jeff Bezos spoke in Seattle",
            "expected": {
                "person": "Jeff Bezos",
                "organization": "Amazon",
                "location": "Seattle"
            }
        }
    ]
    
    # Create few-shot prompt
    few_shot_prompt = "Extract the person, organization, and location from the text:\n\n"
    for example in examples:
        few_shot_prompt += f"Text: {example['text']}\n"
        few_shot_prompt += f"Entities: {json.dumps(example['entities'], indent=2)}\n\n"
    
    for case in test_cases:
        prompt = few_shot_prompt + f"Text: {case['text']}\nEntities:"
        
        response = await client.generate(
            prompt=prompt,
            max_tokens=150,
            temperature=0.3
        )
        
        # Extract JSON from response
        try:
            prediction = json.loads(response["choices"][0]["text"].strip())
            for entity_type, expected_value in case["expected"].items():
                assert expected_value.lower() in prediction[entity_type].lower(), \
                    f"Expected {expected_value} in {entity_type}"
        except json.JSONDecodeError:
            pytest.fail("Response is not valid JSON")