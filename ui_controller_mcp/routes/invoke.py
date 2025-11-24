from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

router = APIRouter()


class InvokeRequest(BaseModel):
    tool: str = Field(..., description="Tool name to execute")
    params: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the tool")


class InvokeResponse(BaseModel):
    success: bool
    tool: str
    result: Dict[str, Any] | None = None
    error: str | None = None


@router.post("/invoke", response_model=InvokeResponse)
async def invoke_tool(request: Request, body: InvokeRequest) -> InvokeResponse:
    tool_names = {tool["name"] for tool in request.app.state.tool_definitions}
    if body.tool not in tool_names:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown tool: {body.tool}",
        )

    try:
        result = request.app.state.tool_executor.execute(body.tool, body.params)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    if not result.get("success", False):
        return InvokeResponse(success=False, tool=body.tool, result=None, error=result.get("error") or result.get("message"))

    return InvokeResponse(success=True, tool=body.tool, result=result, error=None)
