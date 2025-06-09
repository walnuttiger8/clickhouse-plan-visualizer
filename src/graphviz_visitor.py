import graphviz

from query_plan import PlanNode, PlanNodeVisitor


class GraphvizVisitor(PlanNodeVisitor[str]):
    def __init__(self, skip_expressions: bool = True):
        self.dot = graphviz.Digraph(
            node_attr={"shape": "box"}, graph_attr={"rankdir": "LR"}
        )
        self.skip_expressions = skip_expressions

    def visit_expression(self, node: "PlanNode") -> str:
        if self.skip_expressions:
            assert len(node.plans) == 1
            return node.plans[0].accept(self)

        return self._default_visit(node)

    def visit_join(self, node: "PlanNode") -> str:
        assert len(node.plans) == 2

        self.dot.node(node.node_id, label=f"{node.node_type}\n{node.description}")

        self.dot.edge(node.plans[0].accept(self), node.node_id, label="left")
        self.dot.edge(node.plans[1].accept(self), node.node_id, label="right")

        return node.node_id

    def visit_union(self, node: "PlanNode") -> str:
        return self._default_visit(node)

    def visit_read_from_merge_tree(self, node: "PlanNode") -> str:
        return self._default_visit(node)

    def visit_read_from_storage(self, node: "PlanNode") -> str:
        return self._default_visit(node)

    def visit_filter(self, node: "PlanNode") -> str:
        return self._default_visit(node)

    def visit_window(self, node: "PlanNode") -> str:
        return self._default_visit(node)

    def visit_sorting(self, node: "PlanNode") -> str:
        return self._default_visit(node)

    def visit_aggregating(self, node: "PlanNode") -> str:
        return self._default_visit(node)

    def _default_visit(self, node: "PlanNode") -> str:
        description = str(node.description)

        # should make it better... someday
        if len(description) > 50:
            description = ""

        self.dot.node(node.node_id, label=f"{node.node_type}\n{description}".strip())

        for child in node.plans:
            self.dot.edge(child.accept(self), node.node_id)

        return node.node_id
