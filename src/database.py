"""Database operations and SQLAlchemy models."""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import create_engine, Column, String, Integer, DateTime, JSON, ForeignKey, Enum, Interval, TypeDecorator
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from .config import settings

# Custom UUID type for SQLite compatibility
class UUID(TypeDecorator):
    """Platform-independent UUID type.
    Uses SQLite-compatible String type internally."""
    
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)

Base = declarative_base()

class ModelRegistry(Base):
    """Model registry table for tracking LLM versions."""
    
    __tablename__ = "model_registry"
    
    model_id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(255), nullable=False)
    model_version = Column(String(100), nullable=False)
    provider_type = Column(String(50), nullable=False)  # Changed from Enum for SQLite compatibility
    provider_name = Column(String(255), nullable=False)
    model_type = Column(String(100), nullable=False)
    model_architecture = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    deprecated_at = Column(DateTime)

    unit_test_runs = relationship("UnitTestRun", back_populates="model")

    def __repr__(self):
        return f"<ModelRegistry(model_name='{self.model_name}', version='{self.model_version}')>"

class UnitTestSuite(Base):
    """Test suite configuration."""
    
    __tablename__ = "unit_test_suites"
    
    suite_id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    suite_name = Column(String(255), nullable=False, unique=True)
    description = Column(String)
    category = Column(String(100), nullable=False)
    priority = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, onupdate=datetime.utcnow)
    
    tests = relationship("UnitTest", back_populates="suite", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UnitTestSuite(name='{self.suite_name}', category='{self.category}')>"

class UnitTest(Base):
    """Unit test configuration."""
    
    __tablename__ = "unit_tests"
    
    test_id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    suite_id = Column(UUID(), ForeignKey('unit_test_suites.suite_id'), nullable=False)
    test_name = Column(String(255), nullable=False)
    test_type = Column(String(100), nullable=False)
    test_description = Column(String)
    input_data = Column(JSON)
    expected_output = Column(JSON)
    compliance_rules = Column(JSON)
    timeout_seconds = Column(Integer, default=30)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, onupdate=datetime.utcnow)
    
    suite = relationship("UnitTestSuite", back_populates="tests")
    test_runs = relationship("UnitTestRun", back_populates="test")

    def __repr__(self):
        return f"<UnitTest(name='{self.test_name}', type='{self.test_type}')>"

class UnitTestRun(Base):
    """Unit test execution results."""
    
    __tablename__ = "unit_test_runs"
    
    run_id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    test_id = Column(UUID(), ForeignKey('unit_tests.test_id'), nullable=False)
    model_id = Column(UUID(), ForeignKey('model_registry.model_id'), nullable=False)
    run_timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), nullable=False)
    execution_time = Column(Interval)
    actual_output = Column(JSON)
    error_message = Column(String)
    stack_trace = Column(String)
    environment_info = Column(JSON)
    
    test = relationship("UnitTest", back_populates="test_runs")
    model = relationship("ModelRegistry", back_populates="unit_test_runs")

    def __repr__(self):
        return f"<UnitTestRun(test='{self.test_id}', status='{self.status}')>"

def init_db():
    """Initialize the database with tables."""
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(engine)
    return engine

def get_session():
    """Get a database session."""
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    return Session()