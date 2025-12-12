import os
from abc import ABC, abstractmethod
from openai import AsyncClient
from fastmcp import Client as MCPClient
from typing import List, Dict, Any, Literal
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log
from functools import lru_cache
import asyncio
import json
import logging
import colorlog

import sys
sys.path.append('.')

from client.utils import parse_tool, TOOL_START_SEQ, TOOL_STOP_SEQ
from client.rag import RAGEngine, ChromaRAG

LOG_FORMAT = '%(log_color)s%(levelname)-8s%(reset)s %(message)s'
colorlog.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class Toolbox:
    def __init__(self, tools: Dict[str, Dict[str, Any]] = {}, rag_cls = None, method: Literal["list_all", "rag", "fetch"] = "list_all", *args, **kwargs):
        self.tools = tools
        self.clients = {}
        self.rag: RAGEngine | None = rag_cls() if rag_cls else None
        self.method = method

        if self.method == "rag" or self.method == "fetch":
            assert self.rag
            self.default_k = kwargs.get("default_k", 3)
        
        if self.method == "fetch":
            tools["retrieve_tools"] = {
                "tool_name": "retrieve_tools",
                "description": "As there are too many tools available, use this tool to find the most relevant tools based on your query and a requested number k.",
                "arguments": {
                    "query": {"type": "str", "description": "A description of the task or requirements used to find relevant tools (e.g. 'I need to add two numbers'; 'I want to know that time is it now')"},
                    "k": {"type": "int", "description": "Maximum number of the most relevant tools to return"}
                },
                "returns": {
                    "type": "list",
                    "description": "A list of up to k tools most relevant to the provided query"
                }
            }
    
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
        if key_name == "retrieve_tools":
            try:
                return self.retrieve_tools(
                    query=arguments["query"],
                    k=arguments.get("k", self.default_k)
                )
            except Exception as e:
                return {
                    "error": e.__str__()
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
                )).content[0].text
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
    
    def get_system_prompt(self):
        SYSTEM_PROMPT = (
            "You are an AI assistant with access to a set of tools (APIs). "
            "When you need to use a tool, invoke it by outputting a JSON object in the following format:\n"
            f"{TOOL_START_SEQ}\n"
            "{\"name\": \"tool_name\", \"arguments\": {\"arg1\": value1, \"arg2\": value2, ...}}\n"
            f"{TOOL_STOP_SEQ}\n"
            "Below is the list of available tools and their descriptions:\n"
        )
        if self.method == "list_all":
            tool_desc_list = [self.__get_desc_of_one_tool(key_name).__str__() for key_name in self.tools]
            SYSTEM_PROMPT += '\n'.join(map(lambda x: f"- {x}", tool_desc_list))
        elif self.method == "rag":
            SYSTEM_PROMPT += '${CHOSEN_TOOLS}'
        elif self.method == "fetch":
            SYSTEM_PROMPT += self.__get_desc_of_one_tool("retrieve_tools").__str__() + '\n'
        else:
            raise NotImplementedError

        return SYSTEM_PROMPT
    
    def register_server(self, server_name: str, server_url: str, desc_path: str):
        with open(desc_path) as f:
            desc = json.load(f)
            for tool_desc in desc:
                assert "tool_name" in tool_desc and "description" in tool_desc
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
                if self.rag:
                    self.rag.write(
                        doc=f"({tool_name}) {tool_desc['description']}",
                        meta_data={
                            "key_name": key_name
                        }
                    )
        
    def retrieve_tools(self, query: str, k: int | None = None) -> List[Dict[str, Any]]:
        assert self.rag, "RAG engine is required."
        if k is None:
            k = self.default_k
        tools_list = []
        results = self.rag.read(query=query, k=k)
        for result in results:
            key_name = result["meta_data"]["key_name"]
            tools_list.append(
                self.__get_desc_of_one_tool(key_name)
            )
        
        return tools_list


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

        system_prompt = self.system_prompt
        if self.toolbox:
            extra_body.update({"stop": TOOL_STOP_SEQ})
            if self.toolbox.method == "rag":
                system_prompt = system_prompt.replace(
                    "${CHOSEN_TOOLS}",
                    "\n".join(map(lambda x: f"- {x}", self.toolbox.retrieve_tools(query=query)))
                )
        # print(system_prompt)
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
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
                if "name" not in tool_calling_req:
                    tool_resp = {
                        "error": (
                            "Tool call format is missing required fields. "
                            "Please provide 'name' and 'arguments' (If needed), e.g.: "
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

    toolbox = Toolbox(rag_cls=ChromaRAG, method="fetch", default_k=3)

    toolbox.register_server(
        server_name="MathServer",
        server_url="http://127.0.0.1:8000/mcp",
        desc_path="server/math_server/desc.json"
    )

    toolbox.register_server(
        server_name="TimeServer",
        server_url="http://127.0.0.1:8001/mcp",
        desc_path="server/time_server/desc.json"
    )

    # print(toolbox.get_system_prompt())

    print(asyncio.run(toolbox.call(key_name="now", arguments={})))

    llm = OpenAIBackend(model="gpt-4o")
    client = AgentClient(
        llm=llm,
        toolbox=toolbox,
        system_prompt=toolbox.get_system_prompt()
    )

    result1 = asyncio.run(client.process_query(query="What is the value of (114.514 + 1919.810) * 114.514 - 1919.810 (round to the thrid decimal place). (You can use `retrieve_tools` to find tools which can help you solve this problem) Output your final answer with ### {Your answer}\n", verbose=True))
    # result2 = asyncio.run(client.process_query(query="What date is it today? (You can use `retrieve_tools` to find tools which can help you solve this problem)\n", verbose=True))
