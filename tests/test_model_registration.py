"""Tests for model registration and uniqueness handling."""

import os
import pytest
import subprocess
from datetime import datetime
from sqlalchemy import text
from src.database import get_session

def test_model_registration_uniqueness():
    """
    Test that model registration properly handles uniqueness constraints:
    1. Test reuse of existing model
    2. Test unique version generation
    3. Test custom version from environment
    """
    session = get_session()
    
    try:
        # Clean up any test models from previous failed runs
        cleanup_query = text("""
            DELETE FROM model_registry 
            WHERE model_name LIKE 'test-model-unique-%'
        """)
        session.execute(cleanup_query)
        session.commit()
        
        # Test 1: First registration should create a new model
        test_name = f"test-model-unique-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        os.environ["MODEL_NAME"] = test_name
        os.environ["MODEL_VERSION"] = "1.0.0-test"
        
        # Run a simple test using subprocess to avoid session conflicts
        subprocess.run(["pytest", "-v", "tests/test_simple.py", "-s"], env=os.environ)
        
        # Verify first registration
        query = text("""
            SELECT COUNT(*) 
            FROM model_registry 
            WHERE model_name = :model_name 
            AND model_version = :model_version
        """)
        count = session.execute(query, {
            'model_name': test_name,
            'model_version': "1.0.0-test"
        }).scalar()
        
        assert count == 1, "First model registration failed"
        
        # Test 2: Second registration should reuse the same model
        subprocess.run(["pytest", "-v", "tests/test_simple.py", "-s"], env=os.environ)
        
        # Verify no duplicate was created
        count = session.execute(query, {
            'model_name': test_name,
            'model_version': "1.0.0-test"
        }).scalar()
        
        assert count == 1, "Model was duplicated instead of being reused"
        
        # Test 3: New version should create new record
        os.environ["MODEL_VERSION"] = "1.0.1-test"
        subprocess.run(["pytest", "-v", "tests/test_simple.py", "-s"], env=os.environ)
        
        # Verify both versions exist
        query = text("""
            SELECT COUNT(DISTINCT model_version) 
            FROM model_registry 
            WHERE model_name = :model_name
        """)
        version_count = session.execute(query, {
            'model_name': test_name
        }).scalar()
        
        assert version_count == 2, "Failed to create new version"
        
        # Test 4: Timestamp-based versioning
        del os.environ["MODEL_VERSION"]  # Remove version to trigger timestamp-based versioning
        subprocess.run(["pytest", "-v", "tests/test_simple.py", "-s"], env=os.environ)
        
        # Verify timestamp version was created
        query = text("""
            SELECT model_version 
            FROM model_registry 
            WHERE model_name = :model_name 
            AND model_version LIKE '1.0.0-%'
        """)
        timestamp_versions = session.execute(query, {
            'model_name': test_name
        }).fetchall()
        
        assert len(timestamp_versions) > 0, "Timestamp-based versioning failed"
        
        # Print summary
        query = text("""
            SELECT model_name, model_version, created_at 
            FROM model_registry 
            WHERE model_name = :model_name 
            ORDER BY created_at DESC
        """)
        results = session.execute(query, {
            'model_name': test_name
        }).fetchall()
        
        print("\nModel Registration Test Results:")
        for result in results:
            print(f"Model: {result[0]}")
            print(f"Version: {result[1]}")
            print(f"Created: {result[2]}")
            print("-" * 50)
            
    finally:
        # Clean up test models
        cleanup_query = text("""
            DELETE FROM model_registry 
            WHERE model_name = :model_name
        """)
        session.execute(cleanup_query, {
            'model_name': test_name
        })
        session.commit()
        session.close()
        
        # Clean up environment
        if "MODEL_NAME" in os.environ:
            del os.environ["MODEL_NAME"]
        if "MODEL_VERSION" in os.environ:
            del os.environ["MODEL_VERSION"]