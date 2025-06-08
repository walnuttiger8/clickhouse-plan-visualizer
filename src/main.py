import os
import json
from typing import Annotated

import fastapi
from fastapi import responses as fastapi_responses
from fastapi import templating as fastapi_templating

import graphviz_visitor
import query_plan

app = fastapi.FastAPI()

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = fastapi_templating.Jinja2Templates(directory=templates_dir)


@app.get("/")
def index(request: fastapi.Request) -> fastapi_responses.HTMLResponse:
    return templates.TemplateResponse(name="index.html.j2", request=request)


@app.post("/render-plan")
def render_plan(plan: Annotated[str, fastapi.Form()], request: fastapi.Request) -> fastapi_responses.HTMLResponse:
    try:
        parsed_plan = json.loads(plan)
    except json.JSONDecodeError:
        return templates.TemplateResponse(
            name="index.html.j2",
            request=request,
            context={"error": "Invalid JSON format. Please check your plan data."}
        )

    try:
        if not parsed_plan or not isinstance(parsed_plan, list) or len(parsed_plan) == 0:
            return templates.TemplateResponse(
                name="index.html.j2",
                request=request,
                context={"error": "Plan data is empty or invalid. Please provide a valid plan."}
            )

        plan_root = query_plan.Plan.model_validate(parsed_plan[0])
    except Exception as e:
        return templates.TemplateResponse(
            name="index.html.j2",
            request=request,
            context={"error": f"Failed to parse plan: {str(e)}"}
        )

    try:
        visitor = graphviz_visitor.GraphvizVisitor()
        plan_root.plan.accept(visitor)
    except Exception as e:
        return templates.TemplateResponse(
            name="index.html.j2",
            request=request,
            context={"error": f"Failed to generate visualization: {str(e)}"}
        )

    return templates.TemplateResponse(
        name="plan.html.j2",
        request=request,
        context={"graph_source": visitor.dot.source},
    )
