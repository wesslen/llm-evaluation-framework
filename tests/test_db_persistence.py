import pytest
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

def test_model_registration_and_test_run():
    """
    Test to verify model registration and test run recording works end-to-end.
    This test should:
    1. Create a database connection
    2. Register a model
    3. Create a test run
    4. Verify all data is persisted
    """
    # Create database connection
    engine = create_engine('sqlite:///database/llm_evaluation.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 1. Register a model
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
        
        # 2. Get an existing test suite and test
        test_query = text("""
            SELECT test_id FROM unit_tests LIMIT 1
        """)
        test_id = session.execute(test_query).scalar()
        
        if not test_id:
            raise Exception("No test found in unit_tests table")
        
        # 3. Create a test run
        run_id = str(uuid.uuid4())
        run_insert = text("""
            INSERT INTO unit_test_runs (
                run_id, test_id, model_id, status,
                execution_time, actual_output
            ) VALUES (
                :run_id, :test_id, :model_id, :status,
                :execution_time, :actual_output
            )
        """)
        
        session.execute(run_insert, {
            'run_id': run_id,
            'test_id': test_id,
            'model_id': model_id,
            'status': 'completed',
            'execution_time': '00:00:01',
            'actual_output': '{"result": "test output"}'
        })
        
        # Commit the transaction
        session.commit()
        
        # 4. Verify the data
        verify_query = text("""
            SELECT 
                (SELECT COUNT(*) FROM model_registry) as model_count,
                (SELECT COUNT(*) FROM unit_test_runs) as run_count
        """)
        
        result = session.execute(verify_query).first()
        assert result[0] > 0, "No models found in registry"
        assert result[1] > 0, "No test runs recorded"
        
    finally:
        session.close()

if __name__ == "__main__":
    test_model_registration_and_test_run()