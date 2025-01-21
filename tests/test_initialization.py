import pytest
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

def test_suite_and_test_initialization():
    """
    Test to verify both test suites and individual tests are properly initialized.
    This test should:
    1. Create a test suite if none exists
    2. Create a test in that suite
    3. Verify both suite and test are persisted
    """
    # Create database connection
    engine = create_engine('sqlite:///database/llm_evaluation.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # First, let's check what we have
        suite_query = text("""
            SELECT COUNT(*) as suite_count,
                   COUNT(DISTINCT category) as categories
            FROM unit_test_suites;
        """)
        
        test_query = text("""
            SELECT COUNT(*) as test_count
            FROM unit_tests;
        """)
        
        suite_counts = session.execute(suite_query).first()
        test_counts = session.execute(test_query).first()
        
        print(f"Initial state - Suites: {suite_counts[0]}, Categories: {suite_counts[1]}, Tests: {test_counts[0]}")
        
        # Create a test suite if none exists
        suite_id = str(uuid.uuid4())
        suite_insert = text("""
            INSERT INTO unit_test_suites (
                suite_id, suite_name, description, category, 
                priority, created_at, modified_at
            ) VALUES (
                :suite_id, :suite_name, :description, :category,
                :priority, :created_at, :modified_at
            )
        """)
        
        session.execute(suite_insert, {
            'suite_id': suite_id,
            'suite_name': 'test-initialization-suite',
            'description': 'Test suite for initialization verification',
            'category': 'initialization',
            'priority': 1,
            'created_at': datetime.utcnow(),
            'modified_at': datetime.utcnow()
        })
        
        # Create a test in this suite
        test_id = str(uuid.uuid4())
        test_insert = text("""
            INSERT INTO unit_tests (
                test_id, suite_id, test_name, test_type,
                test_description, input_data, expected_output,
                created_at, modified_at
            ) VALUES (
                :test_id, :suite_id, :test_name, :test_type,
                :test_description, :input_data, :expected_output,
                :created_at, :modified_at
            )
        """)
        
        session.execute(test_insert, {
            'test_id': test_id,
            'suite_id': suite_id,
            'test_name': 'initialization-test',
            'test_type': 'input_validation',
            'test_description': 'Basic initialization test',
            'input_data': '{"test": "input"}',
            'expected_output': '{"expected": "output"}',
            'created_at': datetime.utcnow(),
            'modified_at': datetime.utcnow()
        })
        
        # Commit the transaction
        session.commit()
        
        # Verify the data was properly inserted
        verify_query = text("""
            SELECT 
                (SELECT COUNT(*) FROM unit_test_suites WHERE suite_id = :suite_id) as suite_exists,
                (SELECT COUNT(*) FROM unit_tests WHERE test_id = :test_id) as test_exists
        """)
        
        result = session.execute(verify_query, {
            'suite_id': suite_id,
            'test_id': test_id
        }).first()
        
        # Final state check
        final_suites = session.execute(suite_query).first()
        final_tests = session.execute(test_query).first()
        print(f"Final state - Suites: {final_suites[0]}, Categories: {final_suites[1]}, Tests: {final_tests[0]}")
        
        assert result[0] == 1, "Test suite was not created"
        assert result[1] == 1, "Test was not created"
        
    finally:
        session.close()

if __name__ == "__main__":
    test_suite_and_test_initialization()