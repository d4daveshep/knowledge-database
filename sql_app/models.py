from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase


class Base(DeclarativeBase):
    pass


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
