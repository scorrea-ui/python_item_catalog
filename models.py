"""
SQLAlchemy ORM models: User, Category, and Item.

Run this module directly to initialise all database tables:
    python models.py
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, relationship

from database import engine


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


class User(Base):
    """Represents a registered user, created automatically on first OAuth login."""

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False, unique=True)
    picture = Column(String(500))


class Category(Base):
    """
    A top-level grouping for items (e.g. Soccer, Hockey).

    Categories are administrator-managed and seeded via lotsofcatalogitems.py.
    They are not created or owned by individual users.
    """

    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)

    items = relationship(
        "Item",
        back_populates="category",
        cascade="all, delete-orphan",
    )

    @property
    def serialize(self):
        """Return a JSON-serialisable dictionary of this category."""
        return {"id": self.id, "name": self.name}


class Item(Base):
    """
    A single catalog entry belonging to a category.

    Every item has an owner (user_id is required). Seeded items are owned
    by the system user created in lotsofcatalogitems.py; items created
    through the web interface are owned by the logged-in user.
    """

    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(1000))
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    category = relationship("Category", back_populates="items")
    user = relationship("User")

    @property
    def serialize(self):
        """Return a JSON-serialisable dictionary of this item."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.name,
        }


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Database tables created successfully.")
