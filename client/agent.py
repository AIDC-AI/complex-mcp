import os
from abc import ABC, abstractmethod
from openai import AsyncClient
from fastmcp import Client as MCPClient
from typing import List, Dict, Any, Literal
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log
import asyncio
import json
import logging
import colorlog

import sys
sys.path.append('.')

from client.utils import parse_tool, TOOL_START_SEQ, TOOL_STOP_SEQ
from client.rag import RAGEngine

LOG_FORMAT = '%(log_color)s%(levelname)-8s%(reset)s %(message)s'
colorlog.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class Toolbox:
    def __init__(self, tools: Dict[str, Dict[str, Any]] = {}):
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
        tool_name = tool["tool_name"]
        server = tool["server"]
        url = server["url"]

        if url not in self.clients:
            self.clients[url] = MCPClient(url)
        
        client = self.clients[url]
        try:
            async with client:
                result = (await client.call_tool(
                    name=tool_name,
                    arguments=arguments
                )).structured_content
                return result
        except Exception as e:
            return {
                "error": e.__str__()
            }
    
    def __get_desc_of_one_tool(self, key_name: str):
        tool = self.tools[key_name]
        tool_desc = {
            "tool_name": key_name,
            "description": tool["description"],
            "arguments": tool["arguments"]
        }
        if "returns" in tool:
            tool_desc["returns"] = tool["returns"]
        return tool_desc
    
    def get_system_prompt(self, method: Literal["list_all", "rag", "fetch"] = "list_all"):
        tool_desc_list = [self.__get_desc_of_one_tool(key_name).__str__() for key_name in self.tools]
        SYSTEM_PROMPT = (
            "You are an AI assistant with access to a set of tools (APIs). "
            "When you need to use a tool, invoke it by outputting a JSON object in the following format:\n"
            f"{TOOL_START_SEQ}\n"
            "{\"name\": \"tool_name\", \"arguments\": {\"arg1\": value1, \"arg2\": value2, ...}}\n"
            f"{TOOL_STOP_SEQ}\n"
            "Below is the list of available tools and their descriptions:\n"
        )
        if method == "list_all":
            SYSTEM_PROMPT += '\n'.join(map(lambda x: f"- {x}", tool_desc_list))
        elif method == "rag":
            SYSTEM_PROMPT += '${CHOSEN_TOOLS}'
        elif method == "fetch":
            raise NotImplementedError
        else:
            raise NotImplementedError

        return SYSTEM_PROMPT
    
    def register_server(self, server_name: str, server_url: str, desc_path: str):
        with open(desc_path) as f:
            desc = json.load(f)
            for tool_desc in desc:
                tool_name = tool_desc["tool_name"]

                key_name = tool_name[:]
                while key_name in self.tools:
                    key_name = f"{server_name}_{key_name}"
                
                self.tools[key_name] = {**tool_desc, **{
                    "server": {
                        "name": server_name,
                        "url": server_url
                    }
                }}

class ChatBackend(ABC):
    @abstractmethod
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
        max_turns: int = 10,
        verbose: bool = False
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
            
            # Only for AIDC AI-Hub Qwen Model
            # if self.toolbox and resp.choices[0].finish_reason == "stop" and \
            #     msg.removesuffix(TOOL_STOP_SEQ).strip().endswith(TOOL_STOP_SEQ):
            #     msg = msg.removesuffix(TOOL_STOP_SEQ)
            
            if verbose:
                print(msg)

            output.append(msg)
            messages.append({
                "role": "assistant",
                "content": msg
            })
            
            if msg.strip().endswith(TOOL_STOP_SEQ) and self.toolbox:
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
                    ))
                format_tool_resp = f"<response>\n{tool_resp.__str__()}\n</response>"

                if verbose:
                    print(format_tool_resp)

                output.append(format_tool_resp)
                messages.append({
                    "role": "user",
                    "content": format_tool_resp
                })
            else:
                break # quit

        return '\n'.join(output)
        

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    toolbox = Toolbox()

    toolbox.register_server(
        server_name="MathServer",
        server_url="http://127.0.0.1:8000/mcp",
        desc_path="server/math_server/desc.json"
    )

    llm = OpenAIBackend(model="gpt-4o")
    client = AgentClient(
        llm=llm,
        toolbox=toolbox,
        system_prompt=toolbox.get_system_prompt()
    )

    result = asyncio.run(client.process_query(query="What is the value of (114.514 + 1919.810) * 114.514 - 1919.810 (round to the thrid decimal place). Output your final answer with ### {Your answer}\n", verbose=True))

    print(result)
