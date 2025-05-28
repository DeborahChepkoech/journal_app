from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.schema import Table
import datetime


Base = declarative_base()

entry_tag_association = Table(
    'entry_tag_association', Base.metadata,
    Column('entry_id', Integer, ForeignKey('entries.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Entry(Base):
    """Represents a single journal entry."""
    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow)

    
    tags = relationship(
        'Tag',
        secondary=entry_tag_association,
        back_populates='entries'
    )

    def __repr__(self):
        return f"<Entry(id={self.id}, title='{self.title}', date='{self.date.strftime('%Y-%m-%d %H:%M')}')>"

    def display(self):
        """Returns a formatted string for displaying an entry."""
        tag_names = ", ".join([tag.name for tag in self.tags]) if self.tags else "No Tags"
        return (
            f"\n--- Entry ID: {self.id} ---\n"
            f"Title: {self.title}\n"
            f"Date: {self.date.strftime('%Y-%m-%d %H:%M')}\n"
            f"Tags: {tag_names}\n"
            f"Content:\n{self.content}\n"
            f"-------------------------"
        )

class Tag(Base):
    """Represents a tag for organizing journal entries."""
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    entries = relationship(
        'Entry',
        secondary=entry_tag_association,
        back_populates='tags'
    )

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"