import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def test_database_state():
    """
    Test to verify the actual state of the database schema and data.
    This will:
    1. Check what tables actually exist
    2. Query only existing tables for their content
    """
    engine = create_engine('sqlite:///database/llm_evaluation.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # First, get list of tables that actually exist
        existing_tables_query = text("""
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' 
            AND name NOT LIKE 'sqlite_%'
        """)
        
        existing_tables = [row[0] for row in session.execute(existing_tables_query)]
        print("\nExisting tables:", existing_tables)
        
        # Check content of existing tables
        results = {}
        for table in existing_tables:
            # Get column names
            columns_query = text(f"PRAGMA table_info({table})")
            columns = [row[1] for row in session.execute(columns_query)]
            print(f"\nColumns in {table}:", columns)
            
            # Get row count
            count_query = text(f"SELECT COUNT(*) FROM {table}")
            count = session.execute(count_query).scalar()
            results[table] = {
                'row_count': count,
                'columns': columns
            }
            
            # If table has data, show a sample row
            if count > 0:
                sample_query = text(f"SELECT * FROM {table} LIMIT 1")
                sample = session.execute(sample_query).first()
                print(f"\nSample row from {table}:")
                print(dict(zip(columns, sample)))
        
        # Print summary
        print("\nTable statistics:")
        for table, info in results.items():
            print(f"{table}: {info['row_count']} rows, {len(info['columns'])} columns")
            
        return results
            
    finally:
        session.close()

if __name__ == "__main__":
    test_database_state()