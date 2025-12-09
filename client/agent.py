import os
from openai import AsyncClient
from fastmcp import Client as MCPClient
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log
import asyncio
import logging
import colorlog

import sys
sys.path.append('.')

from client.utils import parse_tool, TOOL_START_SEQ, TOOL_STOP_SEQ

LOG_FORMAT = '%(log_color)s%(levelname)-8s%(reset)s %(message)s'
colorlog.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class Toolbox:
    def __init__(self, tools: Dict[str, Dict[str, Any]]):
        self.tools = tools
        self.clients = {}
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def call(
        self,
        key_name: str,
        arguments: Dict[str, Any]
    ):
        if key_name not in self.tools:
            return {
                "error": f"This tool `{key_name}` doesn't exist."
            }
        tool = self.tools[key_name]
        tool_name = tool["name"]
        server = tool["server"]
        url = server["url"]

        if url not in self.clients:
            self.clients[url] = MCPClient(url)
        
        client = self.clients[url]
        async with client:
            result = await client.call_tool(
                name=tool_name,
                arguments=arguments
            )
            return result
    
    def __get_desc_of_one_tool(self, key_name: str):
        tool = self.tools[key_name]
        return {
            "tool_name": key_name,
            "description": tool["description"],
            "arguments": tool["arguments"]
        }
    
    def get_system_prompt(self, list_all: bool = True):
        tool_desc_list = [self.__get_desc_of_one_tool(key_name).__str__() for key_name in self.tools]
        SYSTEM_PROMPT = (
            "You are an AI assistant with access to a set of tools (APIs). "
            "When you need to use a tool, invoke it by outputting a JSON object in the following format:\n"
            f"{TOOL_START_SEQ}\n"
            "{\"name\": \"tool_name\", \"arguments\": {\"arg1\": value1, \"arg2\": value2}}\n"
            f"{TOOL_STOP_SEQ}\n"
            "Below is the list of available tools and their descriptions:\n"
        )
        if list_all:
            SYSTEM_PROMPT += '\n'.join(tool_desc_list)
        else:
            raise NotImplementedError

        return SYSTEM_PROMPT

class ChatBackend:
    async def chat(self, *_, **__) -> Dict[str, Any]:
        raise NotImplemented

class OpenAIBackend(ChatBackend):
    def __init__(self, model: str):
        super().__init__()
        self.model = model
        self.client = AsyncClient(
            api_key=os.environ["OPENAI_API_KEY"],
            base_url=os.environ["OPENAI_BASE_URL"]
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def chat(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int = 10000,
        extra_body: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_completion_tokens": max_tokens,
            **extra_body
        }
        resp = await self.client.chat.completions.create(**payload)

        return resp


class AgentClient:
    def __init__(
        self,
        llm: OpenAIBackend,
        toolbox: Toolbox | None = None,
        system_prompt: str | None = None
    ):
        self.llm = llm
        self.toolbox = toolbox
        self.system_prompt = system_prompt
    
    async def process_query(
        self,
        query: str,
        max_turns: int = 10
    ) -> str:
        messages = []
        output = []
        extra_body = {}

        if self.toolbox:
            extra_body.update({"stop": TOOL_STOP_SEQ})
        
        if self.system_prompt:
            messages.append({
                "role": "system",
                "content": self.system_prompt
            })
        messages.append({
            "role": "user",
            "content": query
        })
        for _ in range(max_turns):
            resp = await self.llm.chat(messages)
            msg: str = resp.choices[0].message.content
            if self.toolbox and resp.choices[0].finish_reason == "stop" and \
                TOOL_START_SEQ in msg and not msg.endswith(TOOL_STOP_SEQ):
                msg += TOOL_STOP_SEQ
            
            print(msg)

            output.append(msg)
            messages.append({
                "role": "assistant",
                "content": msg
            })
            
            if msg.endswith(TOOL_STOP_SEQ) and self.toolbox:
                tool_calling_req = parse_tool(msg)
                if "name" not in tool_calling_req or "arguments" not in tool_calling_req:
                    tool_resp = {
                        "error": (
                            "Tool call format is missing required fields. "
                            "Please provide both 'name' and 'arguments', e.g.: "
                            "{'name': 'tool_name', 'arguments': {'arg1': 'val1', 'arg2': 'val2', ...}}"
                        )
                    }
                else:
                    tool_resp = (await self.toolbox.call(
                        tool_calling_req["name"],
                        tool_calling_req["arguments"]
                    )).structured_content
                format_tool_resp = f"<response>\n{tool_resp.__str__()}\n</response>"

                output.append(format_tool_resp)
                messages.append({
                    "role": "user",
                    "content": format_tool_resp
                })
            else:
                break # quit

        return '\n'.join(output)
        

if __name__ == "__main__":
    toolbox = Toolbox({
        "add": {
            "name": "add",
            "description": "Adds two numbers (a, b) together. Return the value of a + b.",
            "arguments": {
                "a": "The first float number",
                "b": "The second float number"
            },
            "server": {
                "name": "DummyServer",
                "url": "http://127.0.0.1:8000/mcp"
            }
        }
    })

    llm = OpenAIBackend(model="qwen2.5-max")
    client = AgentClient(
        llm=llm,
        toolbox=toolbox,
        system_prompt=toolbox.get_system_prompt()
    )

    result = asyncio.run(client.process_query(query="What is the sum of 114.514 and 1919.810"))

    print(result)
