#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Antigravity (AGY) adapter for the Trellis shared hooks.

AGY hooks use camelCase payloads and ``injectSteps`` / ``decision`` + ``overwrite``
outputs, while Trellis ships Claude-shaped shared hooks in ``.agent/hooks/``.
This adapter translates between the two protocols and skips main-session
``session-start`` and ``workflow-state`` injections inside AGY subagent
conversations.

Usage (from hooks.json, cwd = .agent/):
    python3 -B -X utf8 hooks/trellis_agy.py session-start|workflow-state|subagent

On failure, context hooks return ``{}`` and tool hooks return ``{"decision": "allow"}``.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
HOOK_DIR = Path(__file__).resolve().parent
PLATFORM = "antigravity"
TRELLIS_AGENTS = ("trellis-implement", "trellis-check", "trellis-research")
HOOK_TIMEOUT_SECONDS = 8

# The shared hooks detect their host from these variables before reading
# the payload; drop them so an inherited value cannot claim the session.
_HOST_PROJECT_DIR_ENV = (
    "CLAUDE_PROJECT_DIR",
    "QODER_PROJECT_DIR",
    "CODEBUDDY_PROJECT_DIR",
    "FACTORY_PROJECT_DIR",
    "CURSOR_PROJECT_DIR",
    "GEMINI_PROJECT_DIR",
    "KIRO_PROJECT_DIR",
    "COPILOT_PROJECT_DIR",
    "TRAE_PROJECT_DIR",
    "ZCODE_PROJECT_DIR",
)


def _read_payload() -> dict[str, Any]:
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except (json.JSONDecodeError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _project_root() -> Path | None:
    root = HOOK_DIR.parent.parent  # <repo>/.agent/hooks -> <repo>
    return root.resolve() if (root / ".trellis").is_dir() else None


def _is_subagent_session(payload: dict[str, Any]) -> bool:
    """Return True when the conversation is registered as a parent's subagent.

    AGY writes the initial parent message and parent subagent record before
    child hooks run. Any missing directory or parse error fails open (False).
    """
    conversation_id = payload.get("conversationId")
    artifact_dir = payload.get("artifactDirectoryPath")
    if not isinstance(conversation_id, str) or not conversation_id:
        return False
    if not isinstance(artifact_dir, str) or not artifact_dir:
        return False
    if Path(conversation_id).name != conversation_id or conversation_id in (".", ".."):
        return False

    artifact_path = Path(artifact_dir)
    messages_dir = artifact_path / ".system_generated" / "messages"
    if not messages_dir.is_dir():
        return False

    brain_root = artifact_path.parent
    seen_senders: set[str] = set()
    for msg_path in messages_dir.glob("*.json"):
        if msg_path.name == "read.json":
            continue
        try:
            msg = json.loads(msg_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, ValueError):
            continue
        if not isinstance(msg, dict) or msg.get("recipient") != conversation_id:
            continue
        sender = msg.get("sender")
        if (
            not isinstance(sender, str)
            or not sender
            or sender in seen_senders
            or Path(sender).name != sender
            or sender in (".", "..")
        ):
            continue
        seen_senders.add(sender)
        record_path = brain_root / sender / ".system_generated" / "subagents" / f"{conversation_id}.json"
        if not record_path.is_file():
            continue
        try:
            record = json.loads(record_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, ValueError):
            continue
        if isinstance(record, dict) and record.get("conversationId") == conversation_id:
            return True
    return False


def _trellis_payload(payload: dict[str, Any], root: Path, **extra: Any) -> dict[str, Any]:
    data: dict[str, Any] = {"cwd": str(root), "platform": PLATFORM}
    conversation_id = payload.get("conversationId")
    if isinstance(conversation_id, str) and conversation_id:
        data["conversation_id"] = conversation_id
    prompt = payload.get("lastUserInput")
    if isinstance(prompt, str):
        data["prompt"] = prompt
    data.update(extra)
    return data


def _run_hook(script: str, data: dict[str, Any], root: Path) -> dict[str, Any] | None:
    env = {k: v for k, v in os.environ.items() if k not in _HOST_PROJECT_DIR_ENV}
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, "-B", "-X", "utf8", str(HOOK_DIR / script)],
        input=json.dumps(data, ensure_ascii=False),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(root),
        env=env,
        timeout=HOOK_TIMEOUT_SECONDS,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    output = json.loads(result.stdout)
    return output if isinstance(output, dict) else None


def _additional_context(output: dict[str, Any] | None) -> str:
    if not output:
        return ""
    specific = output.get("hookSpecificOutput")
    if isinstance(specific, dict):
        context = specific.get("additionalContext")
        if isinstance(context, str):
            return context
    return ""


def handle_session_start(payload: dict[str, Any], root: Path) -> dict[str, Any]:
    if _is_subagent_session(payload):
        return {}
    context = _additional_context(
        _run_hook("session-start.py", _trellis_payload(payload, root), root)
    )
    if not context:
        return {}
    return {"injectSteps": [{"systemMessage": {"systemMessage": context}}]}


def handle_workflow_state(payload: dict[str, Any], root: Path) -> dict[str, Any]:
    # Emit the workflow-state breadcrumb once per turn (before the first model call).
    if payload.get("invocationNum", 0) != 0 or _is_subagent_session(payload):
        return {}
    context = _additional_context(
        _run_hook("inject-workflow-state.py", _trellis_payload(payload, root), root)
    )
    if not context:
        return {}
    return {"injectSteps": [{"systemMessage": {"systemMessage": context}}]}


PRE_TOOL_NOOP: dict[str, Any] = {"decision": "allow"}
PRE_TOOL_EVENTS = ("subagent",)


def handle_subagent(payload: dict[str, Any], root: Path) -> dict[str, Any]:
    tool_call = payload.get("toolCall")
    args = tool_call.get("args") if isinstance(tool_call, dict) else None
    if not isinstance(args, dict) or args.get("TypeName") not in TRELLIS_AGENTS:
        return PRE_TOOL_NOOP
    data = _trellis_payload(
        payload,
        root,
        tool_name="Task",
        tool_input={
            "subagent_type": args["TypeName"],
            "prompt": args.get("Prompt", ""),
        },
    )
    output = _run_hook("inject-subagent-context.py", data, root) or {}
    updated = output.get("updatedInput")
    prompt = updated.get("prompt") if isinstance(updated, dict) else None
    if not isinstance(prompt, str) or not prompt or prompt == args.get("Prompt"):
        return PRE_TOOL_NOOP
    return {"decision": "allow", "overwrite": {"Prompt": prompt}}


HANDLERS = {
    "session-start": handle_session_start,
    "workflow-state": handle_workflow_state,
    "subagent": handle_subagent,
}


def main() -> int:
    event = sys.argv[1] if len(sys.argv) > 1 else ""
    payload = _read_payload()
    is_pre_tool = event in PRE_TOOL_EVENTS or payload.get("hookEventName") == "PreToolUse"
    default_out: dict[str, Any] = PRE_TOOL_NOOP if is_pre_tool else {}
    if os.environ.get("TRELLIS_HOOKS") == "0" or os.environ.get("TRELLIS_DISABLE_HOOKS") == "1":
        print(json.dumps(default_out, ensure_ascii=False))
        return 0

    handler = HANDLERS.get(event)
    output: dict[str, Any] = default_out
    try:
        root = _project_root()
        if handler is not None and root is not None:
            output = handler(payload, root)
    except Exception:
        output = default_out
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
