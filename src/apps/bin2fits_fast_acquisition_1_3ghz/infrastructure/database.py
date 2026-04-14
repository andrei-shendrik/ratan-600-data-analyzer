import enum
import uuid

from sqlalchemy import Column, String, Enum, DateTime, Uuid, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from src.ratan_600_data_analyzer.logging.logger_configurator import get_logger

logger = get_logger(__name__)

Base = declarative_base()

class ProcessingStatus(enum.Enum):
    UNPROCESSED = "unprocessed"
    SUCCESS = "success"
    FAILED = "failed"


class FastAcquisition1To3GHzRaw(Base):
    __tablename__ = 'fast_acquisition_1_3ghz_raw'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bin_path_filename = Column(String, nullable=False)
    bin_filename = Column(String, unique=True, nullable=False)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.UNPROCESSED)
    fits_path_filename = Column(String, nullable=True)
    fits_filename = Column(String, unique=True, nullable=True)
    comment = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

def init_db(db_url: str):
    try:
        engine = create_engine(db_url)
        Base.metadata.create_all(engine)
    except Exception as e:
        logger.critical(f"Error database initialization: {e}")
        raise