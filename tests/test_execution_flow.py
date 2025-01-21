import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime

def test_complete_execution_flow():
    """
    Test the complete execution flow:
    1. Register a model
    2. Execute a test
    3. Record results
    This simulates what should happen in the CI/CD pipeline.
    """
    engine = create_engine('sqlite:///database/llm_evaluation.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Step 1: Register a model
        model_id = str(uuid.uuid4())
        model_insert = text("""
            INSERT INTO model_registry (
                model_id, model_name, model_version, provider_type,
                provider_name, model_type, created_at
            ) VALUES (
                :model_id, :model_name, :model_version, :provider_type,
                :provider_name, :model_type, :created_at
            )
        """)
        
        session.execute(model_insert, {
            'model_id': model_id,
            'model_name': 'test-model',
            'model_version': '1.0.0',
            'provider_type': 'on_prem_api',
            'provider_name': 'test-provider',
            'model_type': 'text-generation',
            'created_at': datetime.utcnow()
        })
        
        # Step 2: Get existing test
        test_query = text("""
            SELECT test_id, suite_id 
            FROM unit_tests 
            LIMIT 1
        """)
        test_result = session.execute(test_query).first()
        test_id = test_result[0]
        suite_id = test_result[1]
        
        # Step 3: Create a test run
        run_id = str(uuid.uuid4())
        run_insert = text("""
            INSERT INTO unit_test_runs (
                run_id, test_id, model_id, run_timestamp,
                status, execution_time, actual_output
            ) VALUES (
                :run_id, :test_id, :model_id, :run_timestamp,
                :status, :execution_time, :actual_output
            )
        """)
        
        session.execute(run_insert, {
            'run_id': run_id,
            'test_id': test_id,
            'model_id': model_id,
            'run_timestamp': datetime.utcnow(),
            'status': 'completed',
            'execution_time': '00:00:01',
            'actual_output': '{"result": "test output"}'
        })
        
        # Step 4: Record test results
        result_id = str(uuid.uuid4())
        result_insert = text("""
            INSERT INTO test_results (
                result_id, run_id, test_name, result_value,
                pass_fail, execution_time, created_at
            ) VALUES (
                :result_id, :run_id, :test_name, :result_value,
                :pass_fail, :execution_time, :created_at
            )
        """)
        
        session.execute(result_insert, {
            'result_id': result_id,
            'run_id': run_id,
            'test_name': 'test-execution',
            'result_value': '{"output": "test result"}',
            'pass_fail': True,
            'execution_time': '00:00:01',
            'created_at': datetime.utcnow()
        })
        
        # Commit all changes
        session.commit()
        
        # Verify final state
        verification_query = text("""
            SELECT 
                (SELECT COUNT(*) FROM model_registry) as models,
                (SELECT COUNT(*) FROM unit_test_runs) as runs,
                (SELECT COUNT(*) FROM test_results) as results
        """)
        
        counts = session.execute(verification_query).first()
        print(f"\nFinal state:")
        print(f"Models: {counts[0]}")
        print(f"Test runs: {counts[1]}")
        print(f"Test results: {counts[2]}")
        
        assert counts[0] > 0, "No models registered"
        assert counts[1] > 0, "No test runs recorded"
        assert counts[2] > 0, "No test results recorded"
        
    finally:
        session.close()

if __name__ == "__main__":
    test_complete_execution_flow()