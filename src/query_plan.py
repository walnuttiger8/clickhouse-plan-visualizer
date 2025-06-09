import abc
import typing as t
from enum import Enum

from pydantic import BaseModel, Field


def _to_ch_format(string: str) -> str:
    return " ".join((part.title() for part in string.split("_")))


T = t.TypeVar("T")


class PlanNodeVisitor(abc.ABC, t.Generic[T]):
    @abc.abstractmethod
    def visit_expression(self, node: "PlanNode") -> T: ...

    @abc.abstractmethod
    def visit_join(self, node: "PlanNode") -> T: ...

    @abc.abstractmethod
    def visit_union(self, node: "PlanNode") -> T: ...

    @abc.abstractmethod
    def visit_read_from_merge_tree(self, node: "PlanNode") -> T: ...

    @abc.abstractmethod
    def visit_read_from_storage(self, node: "PlanNode") -> T: ...

    @abc.abstractmethod
    def visit_filter(self, node: "PlanNode") -> T: ...

    @abc.abstractmethod
    def visit_window(self, node: "PlanNode") -> T: ...

    @abc.abstractmethod
    def visit_sorting(self, node: "PlanNode") -> T: ...

    @abc.abstractmethod
    def visit_aggregating(self, node: "PlanNode") -> T: ...


class BaseNode(BaseModel):
    class Config:
        alias_generator = _to_ch_format


class IndexType(Enum):
    MIN_MAX = "MinMax"
    PARTITION = "Partition"
    PRIMARY_KEY = "PrimaryKey"
    SKIP = "Skip"


class PlanIndex(BaseNode):
    type: IndexType
    name: t.Optional[str] = None
    keys: t.Optional[t.List[str]] = None
    condition: t.Optional[str] = None
    description: t.Optional[str] = None
    initial_parts: t.Optional[int] = None
    selected_parts: t.Optional[int] = None
    initial_granules: t.Optional[int] = None
    selected_granules: t.Optional[int] = None


class PlanNode(BaseNode):
    node_type: str
    node_id: str
    description: t.Optional[str] = None
    plans: t.List["PlanNode"] = Field(default_factory=list)
    indexes: t.List["PlanIndex"] = Field(default_factory=list)

    def accept(self, visitor: PlanNodeVisitor[T]) -> T:
        if self.node_type == "Join":
            return visitor.visit_join(self)
        elif self.node_type == "Expression":
            return visitor.visit_expression(self)
        elif self.node_type == "Union":
            return visitor.visit_union(self)
        elif self.node_type == "ReadFromMergeTree":
            return visitor.visit_read_from_merge_tree(self)
        elif self.node_type == "ReadFromStorage":
            return visitor.visit_read_from_storage(self)
        elif self.node_type == "Filter":
            return visitor.visit_filter(self)
        elif self.node_type == "Window":
            return visitor.visit_window(self)
        elif self.node_type == "Sorting":
            return visitor.visit_sorting(self)
        elif self.node_type == "Aggregating":
            return visitor.visit_aggregating(self)
        else:
            raise NotImplementedError(
                f"accept not implemented for node_type={self.node_type}"
            )


class Plan(BaseNode):
    plan: PlanNode
