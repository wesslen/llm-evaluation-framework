"""Database initialization and management script."""

import argparse
import logging
import sqlite3
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseInitializer:
    def __init__(self, db_path: str = "database/llm_evaluation.db"):
        self.db_path = Path(db_path)
        self.schema_path = Path("database/migrations/001_initial_schema.sql")
        
    def ensure_directory(self) -> None:
        """Ensure the database directory exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection with proper settings."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
        
    def drop_all_tables(self, conn: sqlite3.Connection) -> None:
        """Drop all existing tables in reverse order of dependencies."""
        logger.info("Dropping existing tables...")
        
        # Get all tables in the database
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        tables = cursor.fetchall()
        
        # Temporarily disable foreign key constraints
        conn.execute("PRAGMA foreign_keys = OFF")
        
        try:
            for (table_name,) in tables:
                logger.info(f"Dropping table: {table_name}")
                conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            
            conn.commit()
        finally:
            # Re-enable foreign key constraints
            conn.execute("PRAGMA foreign_keys = ON")
    
    def create_tables(self, conn: sqlite3.Connection) -> None:
        """Create all tables from the schema file."""
        logger.info("Creating database tables...")
        
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
            
        with open(self.schema_path, 'r') as f:
            schema_sql = f.read()
            
        # Split the schema into individual statements
        # This handles the case where some statements might already be executed
        statements = schema_sql.split(';')
        
        for statement in statements:
            statement = statement.strip()
            if statement:  # Skip empty statements
                try:
                    conn.execute(statement + ';')
                except sqlite3.OperationalError as e:
                    if "already exists" not in str(e):
                        raise
                    logger.warning(f"Table already exists: {e}")
        
        conn.commit()

    def initialize_database(self, drop_existing: bool = False) -> None:
        """Initialize the database with the schema."""
        self.ensure_directory()
        
        with self.get_connection() as conn:
            if drop_existing:
                self.drop_all_tables(conn)
            self.create_tables(conn)
            
        logger.info("Database initialization completed successfully.")

def main():
    parser = argparse.ArgumentParser(description="Initialize the LLM evaluation database")
    parser.add_argument('--drop', action='store_true', help="Drop existing tables before creation")
    args = parser.parse_args()
    
    try:
        initializer = DatabaseInitializer()
        initializer.initialize_database(drop_existing=args.drop)
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    main()