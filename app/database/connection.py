from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config.settings import settings
from app.models.database_models import Base

# Create SQLite engine
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency for obtaining database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import inspect, text

def init_db_schema():
    """Create all tables in database if they do not exist and ensure schema migration."""
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)
            if "users" in inspector.get_table_names():
                columns = [c["name"] for c in inspector.get_columns("users")]
                if "email" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR"))
                if "password_hash" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR"))
                if "token" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN token VARCHAR"))
                if "current_streak" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN current_streak INTEGER DEFAULT 0"))
                if "longest_streak" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN longest_streak INTEGER DEFAULT 0"))
                if "last_active_date" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN last_active_date VARCHAR"))
                if "is_onboarded" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_onboarded BOOLEAN DEFAULT 0"))
                if "user_level" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN user_level VARCHAR DEFAULT 'Beginner'"))
                if "diagnostic_score" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN diagnostic_score FLOAT DEFAULT 0.0"))
                conn.commit()
    except Exception as e:
        print(f"Schema migration notice: {e}")
