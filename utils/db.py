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


def get_roast_styles():
    with SessionLocal() as session:
        result = session.execute(
            text(
                "select * from roast_my_code.roast_style"
            ),
        )
        return [dict(row._mapping) for row in result.fetchall()]


def insert_roast(roast_style, code: str = None, github_user: str = None, github_repository: str = None) -> int:
    with SessionLocal() as session:
        result = session.execute(
            text(
                "INSERT INTO roast_my_code.roast (roast_style, code, github_user, github_repository)"
                " VALUES (:roast_style, :code, :github_user, :github_repository) RETURNING id"
            ),
            {"roast_style": roast_style, "code": code, "github_user": github_user, "github_repository": github_repository},
        )
        session.commit()
        return result.scalar_one()


def insert_clapback(roast_id: int, llm_response: str, audio_url: str = None) -> int:
    """Insert a new clapback and return its ID."""
    with SessionLocal() as session:
        result = session.execute(
            text(
                "INSERT INTO roast_my_code.clapback (roast_id, llm_response, audio_url)"
                " VALUES (:roast_id, :llm_response, :audio_url) RETURNING id"
            ),
            {"roast_id": roast_id, "llm_response": llm_response, "audio_url": audio_url},
        )
        session.commit()
        return result.scalar_one()


def get_clapback(clapback_id: int):
    """Retrieve a clapback by ID, returning a dict or None."""
    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT id, llm_response, audio_url, create_ts"
                " FROM roast_my_code.clapback WHERE id = :id"
            ),
            {"id": clapback_id},
        ).mappings().first()
    return dict(row) if row else None
  

def get_remaining_credits() -> int:
    """Get the current number of remaining credits."""
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT remaining FROM roast_my_code.payitforward_credits WHERE id = 1")
        ).scalar_one_or_none()
    return int(result) if result is not None else 0


def get_latest_roasts():
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT r.*, c.llm_response
                 FROM roast_my_code.roast r
                 INNER JOIN roast_my_code.clapback c on c.id=r.id
                 ORDER BY create_ts DESC FETCH FIRST 3 ROWS ONLY
            """)
        )
    return result.fetchall()


def increment_credits(amount: int = 1) -> int:
    """Increase credits by the given amount and return new total."""
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE roast_my_code.payitforward_credits SET remaining=remaining + :amt WHERE id=1"),
            {"amt": amount},
        )
    return get_remaining_credits()

def decrement_credits() -> bool:
    """Attempt to decrement a credit. Returns True if successful, False if none left."""
    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT remaining FROM roast_my_code.payitforward_credits WHERE id = 1 FOR UPDATE")
        ).scalar_one_or_none()
        if row is None or row <= 0:
            return False
        conn.execute(
            text("UPDATE roast_my_code.payitforward_credits SET remaining = remaining - 1 WHERE id = 1")
        )
        return True
  
def reset_credits() -> int:
    """Reset the pay-it-forward credits to zero and return new total."""
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE roast_my_code.payitforward_credits SET remaining = 0 WHERE id = 1")
        )
    return get_remaining_credits()