import json
from typing import Annotated

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import graphviz_visitor
import query_plan

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/")
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(name="index.html.j2", request=request)


@app.post("/render-plan")
def render_plan(plan: Annotated[str, Form()], request: Request) -> HTMLResponse:
    parsed_plan = json.loads(plan)

    plan_root = query_plan.Plan.model_validate(parsed_plan[0])

    visitor = graphviz_visitor.GraphvizVisitor()

    plan_root.plan.accept(visitor)

    return templates.TemplateResponse(
        name="plan.html.j2",
        request=request,
        context={"graph_source": visitor.dot.source},
    )
