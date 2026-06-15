"""
Sequential Thinking MCP Server
动态反思式结构化推理工具，支持思维链分支、修订和多步分解
"""

import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


@dataclass
class Thought:
    content: str
    thought_number: int
    total_thoughts: int
    next_thought_needed: bool
    is_revision: bool = False
    revises_thought: Optional[int] = None
    branch_from_thought: Optional[int] = None
    branch_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class SEQUENTIAL_THINKINGMCPServer(BaseMCPServer):

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._thoughts: List[Thought] = []
        self._branches: Dict[str, List[Thought]] = {}
        super().__init__(config)

    def register_tools(self) -> None:
        self._register_tool(MCPTool(
            name="sequential_thinking",
            description=(
                "动态反思式问题求解工具。通过编号思维序列进行结构化推理，"
                "支持分支(branching)、修订(revision)和动态调整步数。"
                "适用于复杂问题分解、多方案对比、逐步推导等场景。"
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "当前思维步骤的内容"
                    },
                    "thoughtNumber": {
                        "type": "integer",
                        "description": "当前思维步骤编号（从1开始）"
                    },
                    "totalThoughts": {
                        "type": "integer",
                        "description": "预估总思维步数（可动态调整）"
                    },
                    "nextThoughtNeeded": {
                        "type": "boolean",
                        "description": "是否还需要下一步思维"
                    },
                    "isRevision": {
                        "type": "boolean",
                        "description": "是否为对之前思维的修订",
                        "default": False
                    },
                    "revisesThought": {
                        "type": "integer",
                        "description": "被修订的思维步骤编号"
                    },
                    "branchFromThought": {
                        "type": "integer",
                        "description": "从哪个思维步骤开始分支"
                    },
                    "branchId": {
                        "type": "string",
                        "description": "分支标识符"
                    },
                    "needsMoreThoughts": {
                        "type": "boolean",
                        "description": "是否需要增加总步数"
                    }
                },
                "required": ["thought", "thoughtNumber", "totalThoughts", "nextThoughtNeeded"]
            },
            capability=ServerCapability.READ
        ))

    def register_resources(self) -> None:
        self._register_resource(MCPResource(
            uri="sequential_thinking://history",
            name="思维历史",
            description="所有已记录的思维步骤"
        ))

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        if tool_name != "sequential_thinking":
            raise ValueError(f"未知工具: {tool_name}")

        thought = Thought(
            content=params["thought"],
            thought_number=params["thoughtNumber"],
            total_thoughts=params["totalThoughts"],
            next_thought_needed=params["nextThoughtNeeded"],
            is_revision=params.get("isRevision", False),
            revises_thought=params.get("revisesThought"),
            branch_from_thought=params.get("branchFromThought"),
            branch_id=params.get("branchId"),
        )

        if thought.branch_id and thought.branch_from_thought:
            if thought.branch_id not in self._branches:
                self._branches[thought.branch_id] = []
            self._branches[thought.branch_id].append(thought)
        else:
            self._thoughts.append(thought)

        if params.get("needsMoreThoughts"):
            thought.total_thoughts += 1

        result = {
            "thoughtNumber": thought.thought_number,
            "totalThoughts": thought.total_thoughts,
            "nextThoughtNeeded": thought.next_thought_needed,
            "branches": list(self._branches.keys()),
            "progress": f"{thought.thought_number}/{thought.total_thoughts}",
        }

        if thought.is_revision and thought.revises_thought:
            result["revised"] = thought.revises_thought

        if not thought.next_thought_needed:
            result["conclusion"] = self._build_summary()

        return result

    async def _read_resource_content(self, resource: MCPResource) -> Any:
        if resource.uri == "sequential_thinking://history":
            return {
                "main_sequence": [
                    {"number": t.thought_number, "content": t.content, "timestamp": t.timestamp}
                    for t in self._thoughts
                ],
                "branches": {
                    bid: [
                        {"number": t.thought_number, "content": t.content}
                        for t in thoughts
                    ]
                    for bid, thoughts in self._branches.items()
                }
            }
        raise ValueError(f"未知资源: {resource.uri}")

    def _build_summary(self) -> Dict[str, Any]:
        return {
            "total_steps": len(self._thoughts),
            "revisions": sum(1 for t in self._thoughts if t.is_revision),
            "branches": len(self._branches),
            "final_thought": self._thoughts[-1].content if self._thoughts else None,
        }
