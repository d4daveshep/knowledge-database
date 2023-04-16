from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)

    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column(index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    owner: Mapped["User"] = relationship(back_populates="items")


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

    def __repr__(self):
        return f"Node(id={self.id}, name={self.name!r})"


class Connection(Base):
    __tablename__ = "connections"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

    subject_id: Mapped[int] = mapped_column(ForeignKey("nodes.id"))
    target_id: Mapped[int] = mapped_column(ForeignKey("nodes.id"))

    subject: Mapped["Node"] = relationship(foreign_keys=[subject_id])
    target: Mapped["Node"] = relationship(foreign_keys=[target_id])

    # target: Mapped["Node"] = relationship()

    def __repr__(self):
        return f"Connection(id={self.id}, name={self.name}, subject_id={self.subject_id}, target_id={self.target_id})"
