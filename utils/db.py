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