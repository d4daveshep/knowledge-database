from typing import Any

from sqlalchemy import ForeignKey, func
from sqlalchemy.ext.hybrid import Comparator, hybrid_property
from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase


class Base(DeclarativeBase):
    pass


class CaseInsensitiveComparator(Comparator[str]):
    """
    Copied this from https://docs.sqlalchemy.org/en/20/orm/extensions/hybrid.html#building-custom-comparators
    """

    def __eq__(self, other: Any) -> bool:  # type: ignore[override]  # noqa: E501
        return func.lower(self.__clause_element__()) == func.lower(other)


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

    def __repr__(self):
        return f"Node(id={self.id}, name={self.name!r})"

    """
     Copied this from https://docs.sqlalchemy.org/en/20/orm/extensions/hybrid.html#building-custom-comparators
     """

    @hybrid_property
    def name_insensitive(self) -> str:
        return self.name.lower()

    @name_insensitive.inplace.comparator
    @classmethod
    def _name_insensitive_comparator(cls) -> CaseInsensitiveComparator:
        return CaseInsensitiveComparator(cls.name)


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

    """
     Copied this from https://docs.sqlalchemy.org/en/20/orm/extensions/hybrid.html#building-custom-comparators
     """

    @hybrid_property
    def name_insensitive(self) -> str:
        return self.name.lower()

    @name_insensitive.inplace.comparator
    @classmethod
    def _name_insensitive_comparator(cls) -> CaseInsensitiveComparator:
        return CaseInsensitiveComparator(cls.name)
