import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from tenacity import retry, stop_after_attempt, wait_fixed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/ace_db")

def init():
    try:
        # Parse the database URL to get the base connection URL (postgres db)
        # Assuming format: postgresql://user:pass@host:port/dbname
        from urllib.parse import urlparse
        
        url = urlparse(DATABASE_URL)
        db_name = url.path[1:]  # Remove leading slash
        
        # Construct URL for the default 'postgres' database
        # We use this to connect and check/create the target database
        postgres_db_url = f"{url.scheme}://{url.username}:{url.password}@{url.hostname}:{url.port}/postgres"
        
        engine = create_engine(postgres_db_url, isolation_level="AUTOCOMMIT")
        
        @retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
        def check_db_connection():
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        
        logger.info("Checking connection to postgres database...")
        check_db_connection()
        logger.info("Connection successful.")
        
        with engine.connect() as conn:
            # Check if target database exists
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
            exists = result.scalar()
            
            if not exists:
                logger.info(f"Database '{db_name}' does not exist. Creating...")
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                logger.info(f"Database '{db_name}' created successfully.")
            else:
                logger.info(f"Database '{db_name}' already exists.")
                
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        # We don't exit here because we want to let the main app try to connect
        # and fail if it must, or maybe the DB was already there and we just failed to check.
        # But usually, if this fails, the app will fail too.
        sys.exit(1)

if __name__ == "__main__":
    init()
