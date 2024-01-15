from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy.types import Time

Base = declarative_base()

class AudioFile(Base):
    __tablename__ = 'audio_files'
    id = Column(Integer, primary_key=True)
    file_path = Column(String, unique=True)
    finished_processing = Column(Integer, default=0)


class TokenText(Base):
    __tablename__ = 'token_text'
    id = Column(Integer, primary_key=True)
    text = Column(String, unique=True)


class Token(Base):
    __tablename__ = 'tokens'
    id = Column(Integer, primary_key=True)
    token_text_id = Column(Integer, ForeignKey('token_text.id'))
    token_text = relationship("TokenText")
    timestamp_from = Column(Time)
    timestamp_to = Column(Time)
    offset_from = Column(Integer)
    offset_to = Column(Integer)
    token_id = Column(Integer)
    audio_file_id = Column(Integer, ForeignKey('audio_files.id'))
    audio_file = relationship("AudioFile")


# relative to the root of the project
DB_PATH = "spclipper/tokens.db"

# Create an engine that stores data in the local directory's database file.
engine = create_engine(f"sqlite:///{DB_PATH}")

# Create all tables in the engine.
Base.metadata.create_all(engine)

print("Database created at {}".format(DB_PATH))