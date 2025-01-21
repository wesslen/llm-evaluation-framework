import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def test_initial_data_state():
    """
    Test to verify the state of initial data in all core tables.
    This will help identify which tables are populated during initialization.
    """
    engine = create_engine('sqlite:///database/llm_evaluation.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check all core tables
        tables = [
            'model_registry',
            'unit_test_suites',
            'unit_tests',
            'unit_test_runs',
            'evaluation_frameworks',
            'test_cases'
        ]
        
        results = {}
        for table in tables:
            count_query = text(f"SELECT COUNT(*) FROM {table}")
            count = session.execute(count_query).scalar()
            results[table] = count
            
        # For tables with data, get sample rows
        for table, count in results.items():
            if count > 0:
                sample_query = text(f"SELECT * FROM {table} LIMIT 1")
                sample = session.execute(sample_query).first()
                print(f"\nSample from {table}:")
                print(sample)
                
        # Print summary
        print("\nTable counts:")
        for table, count in results.items():
            print(f"{table}: {count} rows")
            
        return results
            
    finally:
        session.close()

if __name__ == "__main__":
    test_initial_data_state()