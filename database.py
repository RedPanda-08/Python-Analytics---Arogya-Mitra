from sqlalchemy import create_engine # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore

#Database URL
DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/arogya_mitra_analytics_db"

# SQLAlchemy
engine = create_engine(DATABASE_URL)
# SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()