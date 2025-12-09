from typing import Dict, Any
import json

TOOL_START_SEQ = "<tool>"
TOOL_STOP_SEQ = "</tool>"

def parse_tool(msg: str) -> Dict[str, Any] | None:
    msg = msg.strip()
    start = msg.rfind(TOOL_START_SEQ)
    if start == -1:
        return None
    tool_calling_msg = msg[start + len(TOOL_START_SEQ) :].removesuffix(TOOL_STOP_SEQ).strip()
    tool_calling_req = None
    try:
        tool_calling_req = json.loads(tool_calling_msg)
    except Exception as e:
        return None
    
    return tool_calling_req
