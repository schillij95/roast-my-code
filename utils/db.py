import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Use DATABASE_URL env var or default to localhost Postgres (host=localhost:5031)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5031/postgres"
)

# Create SQLAlchemy engine and session factory
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize database schema
with engine.begin() as conn:
    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS clapbacks (
                id SERIAL PRIMARY KEY,
                llm_response TEXT NOT NULL,
                audio_url TEXT,
                create_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )

def insert_clapback(llm_response: str, audio_url: str = None) -> int:
    """Insert a new clapback and return its ID."""
    with SessionLocal() as session:
        result = session.execute(
            text(
                "INSERT INTO clapbacks (llm_response, audio_url)"
                " VALUES (:llm_response, :audio_url) RETURNING id"
            ),
            {"llm_response": llm_response, "audio_url": audio_url},
        )
        session.commit()
        return result.scalar_one()

def get_clapback(clapback_id: int):
    """Retrieve a clapback by ID, returning a dict or None."""
    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT id, llm_response, audio_url, create_ts"
                " FROM clapbacks WHERE id = :id"
            ),
            {"id": clapback_id},
        ).mappings().first()
    return dict(row) if row else None
  
# Initialize pay-it-forward credits table
with engine.begin() as conn:
    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS payitforward_credits (
                id INT PRIMARY KEY,
                remaining BIGINT NOT NULL
            )
            """
        )
    )
    conn.execute(
        text(
            """
            INSERT INTO payitforward_credits (id, remaining)
            SELECT 1, 0
            WHERE NOT EXISTS (SELECT 1 FROM payitforward_credits WHERE id = 1)
            """
        )
    )

def get_remaining_credits() -> int:
    """Get the current number of remaining credits."""
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT remaining FROM payitforward_credits WHERE id = 1")
        ).scalar_one_or_none()
    return int(result) if result is not None else 0

def increment_credits(amount: int = 1) -> int:
    """Increase credits by the given amount and return new total."""
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO payitforward_credits (id, remaining) VALUES (1, :amt) "
                "ON CONFLICT (id) DO UPDATE SET remaining = payitforward_credits.remaining + :amt"
            ),
            {"amt": amount},
        )
    return get_remaining_credits()

def decrement_credits() -> bool:
    """Attempt to decrement a credit. Returns True if successful, False if none left."""
    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT remaining FROM payitforward_credits WHERE id = 1 FOR UPDATE")
        ).scalar_one_or_none()
        if row is None or row <= 0:
            return False
        conn.execute(
            text("UPDATE payitforward_credits SET remaining = remaining - 1 WHERE id = 1")
        )
        return True