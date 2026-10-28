
import json
import os

from openai import OpenAI
from app.tools import (
    search_policies,
    validate_application,
    create_application_draft,
)

MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")

INSTRUCTIONS = """
You are Rafeeq, an educational municipal food-truck permit assistant.
Reply in the user's language, including Arabic when appropriate.
Use search_policies for questions about policy requirements.
Never invent policy details or applicant information.
The local policy is synthetic educational data, not official Saudi regulation.
Use validate_application to check application information.
Create a draft only when the user explicitly asks to prepare one.
Never claim that an application was officially submitted or approved.
A draft requires human approval. Ask for missing information when necessary.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_policies",
            "description": "Search local synthetic policy documents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search terms for the policy."
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "validate_application",
            "description": "Validate the required fields in an application.",
            "parameters": {
                "type": "object",
                "properties": {
                    "application": {
                        "type": "object",
                        "properties": {
                            "applicant_name": {"type": "string"},
                            "location": {"type": "string"},
                            "activity": {"type": "string"},
                            "contact": {"type": "string"}
                        },
                        "required": [
                            "applicant_name", "location",
                            "activity", "contact"
                        ],
                        "additionalProperties": False
                    }
                },
                "required": ["application"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_application_draft",
            "description": (
                "Prepare a local application draft. "
                "Call only when the user explicitly requests a draft."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "application": {
                        "type": "object",
                        "properties": {
                            "applicant_name": {"type": "string"},
                            "location": {"type": "string"},
                            "activity": {"type": "string"},
                            "contact": {"type": "string"}
                        },
                        "required": [
                            "applicant_name", "location",
                            "activity", "contact"
                        ],
                        "additionalProperties": False
                    }
                },
                "required": ["application"],
                "additionalProperties": False
            }
        }
    }
]

def _run_tool(name, arguments):
    if name == "search_policies":
        return search_policies(arguments["query"])
    if name == "validate_application":
        return validate_application(arguments["application"])
    if name == "create_application_draft":
        return create_application_draft(arguments["application"])
    return {"error": "Unknown tool"}

def run_openrouter_agent(message, max_tool_rounds=4):
    if not message or not message.strip():
        return {"ok": False, "error": "Message cannot be empty."}

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {"ok": False, "error": "OPENROUTER_API_KEY is not set."}

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    messages = [
        {"role": "system", "content": INSTRUCTIONS},
        {"role": "user", "content": message},
    ]
    tool_steps = 0

    try:
        for _ in range(max_tool_rounds + 1):
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
            assistant_message = response.choices[0].message
            calls = assistant_message.tool_calls or []

            if not calls:
                return {
                    "ok": True,
                    "answer": assistant_message.content or "",
                    "tool_steps": tool_steps,
                    "model": response.model,
                }

            messages.append(
                assistant_message.model_dump(exclude_none=True)
            )

            for call in calls:
                try:
                    arguments = json.loads(call.function.arguments)
                    result = _run_tool(call.function.name, arguments)
                except Exception as exc:
                    result = {
                        "error": "Tool execution failed",
                        "detail": str(exc),
                    }

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(
                        result, ensure_ascii=False, default=str
                    ),
                })
                tool_steps += 1

        return {
            "ok": False,
            "error": "Maximum tool rounds reached.",
            "tool_steps": tool_steps,
        }

    except Exception as exc:
        return {
            "ok": False,
            "error": f"{type(exc).__name__}: {str(exc)[:500]}",
            "model": MODEL,
        }
