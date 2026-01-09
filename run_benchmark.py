from client.agent import OpenAIBackend, HumanAnnotator, AgentClient, Toolbox
from benchmark.judge import judge_env
from dotenv import load_dotenv
from argparse import ArgumentParser
from prompt_toolkit import prompt
from typing import Dict, Any
from pathlib import Path
import random
import json

import sys
import os
import yaml
import asyncio

import pandas as pd
from shortuuid import uuid
from datetime import datetime

def parse_toolbox(tool_config_path: str | Path, method: str):
    config = {}
    with open(tool_config_path) as f:
        data = yaml.safe_load(f)
        config["servers"] = data["servers"]

    toolbox = Toolbox(method=method)
    for server in config["servers"]:
        if not server["use"]: continue
        server_args = {
            "server_name": server["name"],
            "server_url": server["url"],
            "desc_path": server.get("desc"),
            "use_sandbox": server.get("use_sandbox", False)
        }
        toolbox.register_server(**server_args)
    
    return toolbox

def parse_query(output: str):
    i = output.find("<query>")
    j = output.find("</query>")
    if i < 0 or i >= j:
        return None
    
    return output[i + len("<query>") : j]

def add_data(query_result: Dict[str, Any]):
    dataset_path = Path("benchmark") / "data" / "data.parquet"
    if os.path.exists(dataset_path):
        df = pd.read_parquet(dataset_path)
    else:
        df = pd.DataFrame()
    new_df = pd.DataFrame(query_result)
    df = pd.concat([df, new_df])

    df.to_parquet(dataset_path)

def gen_instruct_by_human(agent: AgentClient, generate: bool):
    toolbox = agent.toolbox
    method = toolbox.method

    assert method != "provide"
    apps = [app for app in toolbox.servers if app in {"LightTalk", "LightShop", "LightWeather", "LightFlight", "LightStock", "LightNews"}]
    # apps = [app for app in toolbox.servers if app in {"LightShop"}]
    seed = int(prompt("> seed: "))
    level = int(prompt("> level: "))
    query = f"{prompt('> instruct: ')}\nOnce you've completed the task—or if you believe it's unsolvable—output [END] at the end."

    task = agent.process_query(
        query=query,
        max_turns=10000,
        verbose=True,
        stop_tag="[END]",
        env={
            "apps": apps,
            "seed": seed
        }
    )
    
    result = asyncio.run(task)
    print(result["tool_cnt"])

    if generate:
        query_result = {
            "seed": [seed],
            "query": [query],
            "apps": [json.dumps(apps)],
            "level": [level],
            "output": [json.dumps(result["output"])],
            "tool_cnt": [json.dumps(result["tool_cnt"])],
            "gt_env": [json.dumps(result["apps"])]
        }
        ok = prompt(">>> Pass this query? [Y/n] ")
        if ok.strip().lower() == "y":
            add_data(query_result)

INSTRUCT_GEN_PROMPT = """
You are now tasked with designing a challenging problem that rigorously tests a model's tool-calling capabilities and its ability to manage complex interdependencies among multiple tools. The problem must explicitly require the use of the following tools: **$TOOLS** (though other previously mentioned tools may also be used if necessary).

To craft this problem effectively, **begin by simulating the process yourself**: follow the tool-calling rules outlined earlier to gather observations—such as retrieving contact lists, querying store inventories, checking account balances, etc.—until you have sufficient contextual information. Once you've collected enough observations, formulate a problem that satisfies all the criteria below:

1. **State-modifying actions required**: The problem must necessitate calling functions that alter the environment’s state (e.g., `send_message`, `create_group_chat`, `purchase_item`, etc.).

2. **Precise and unambiguous instructions**: Your problem description must be exact and deterministic. For example: “Send a message to Dennis that reads: ‘I spent $199 to buy an AirPods.’” This ensures the expected outcome is clearly verifiable against a fixed rule set.

3. **Non-trivial complexity with interdependent tool calls**: The solution should involve a sequence of tool invocations where later steps depend on the outputs or side effects of earlier ones, creating meaningful logical or temporal dependencies (e.g., checking inventory before purchasing, confirming available funds before completing a transaction, and only then notifying a contact).

4. **Self-validation**: After drafting your problem, attempt to solve it yourself using the allowed tools. If you encounter ambiguities, missing prerequisites, or logical inconsistencies, revise the problem accordingly.

5. **Implicit tool usage**: The final problem must be phrased as a single, coherent, natural-language instruction chain—written as one continuous narrative without bullet points or explicit step-by-step breakdowns—to genuinely test the model’s ability to autonomously plan and sequence actions. It must implicitly require multiple tool calls, including at least one that modifies the environment’s state (e.g., sending a message, making a purchase, creating a group chat, booking an event), but never name or reference any tools, APIs, or technical operations directly.

6. **Iterative refinement with staged output**: During your design process, first present your candidate problem wrapped in `<temp>...</temp>` tags. Then, simulate solving it step by step using the available tools. If you identify any issues—such as missing information, infeasible steps, or unclear phrasing—revise the problem and re-test. Only when you are fully satisfied that it is clear, well-posed, sufficiently complex, and meets all requirements should you output the final version strictly within `<query>...</query>` tags.

In short:  
- Gather necessary information using the provided schema and rules.  
- **Draft an initial version of your problem and enclose it in `<temp>...</temp>`**.
- Attempt to solve it yourself; refine as needed.  
- Once confident the problem is robust and complete, output the polished version exactly as:

<query>
[Your final problem statement here]
</query>
"""

def gen_instruct_by_llm(agent: AgentClient):
    toolbox = agent.toolbox

    softwares = [server_name for server_name in toolbox.servers if toolbox.servers[server_name]["need_session"] and server_name != "LightSystem"]
    external_servers = [server_name for server_name in toolbox.servers if not toolbox.servers[server_name]["need_session"]]

    level = int(prompt("> level: "))
    assert level >= 1
    number = int(prompt("> number: "))
    assert number >= 1

    instructs = []
    for _ in range(number):
        apps = [softwares[0]] + random.sample(softwares[1:], k=level - 1)
        servers = random.sample(external_servers, k=level)

        server_descs = []
        sel_tools = []

        for server_name in apps + servers:
            tools = toolbox.servers[server_name]["tools"]
            
            sel_tools.extend(random.sample(tools, k=level + 2))
            tool_descs = toolbox.get_tool_descs(tools)
            server_descs.append(f"{server_name}:\n{tool_descs}")
        system_prompt = toolbox.get_system_prompt(discard_tools=True) + "\n".join(server_descs)

        agent.set_system_prompt(system_prompt)
        query = INSTRUCT_GEN_PROMPT.replace("$TOOLS", str(sel_tools))
        seed = random.randint(1, 100000)

        task = agent.process_query(
            query=query,
            max_turns=1000,
            verbose=True,
            stop_tag="</query>",
            env={
                "apps": apps,
                "seed": seed
            }
        )

        result = asyncio.run(task)
        output = result["output"]
        query = parse_query(output)
        instructs.append({
            "seed": seed,
            "apps": apps,
            "query": query.strip()
        })

    file_path = Path("benchmark") / "instruct" / f"inst_{uuid()[:8]}.yaml"
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "level": level,
        "instructs": instructs
    }

    with open(file_path, "w") as f:
        yaml.safe_dump(data, f)


def main(args):
    model = args.__getattribute__("model")
    tool_config_path = args.__getattribute__("tool_config")
    custom = args.__getattribute__("custom")
    generate = args.__getattribute__("generate")
    distraction = args.__getattribute__("distraction")

    method = "list_all" if distraction == -1 else "provide"

    toolbox = parse_toolbox(tool_config_path, method) if tool_config_path else None
    if model == "human":
        llm = HumanAnnotator()
    else:
        llm = OpenAIBackend(model=model)
    agent = AgentClient(
        llm=llm,
        toolbox=toolbox,
        system_prompt=toolbox.get_system_prompt() if toolbox else ""
    )

    if custom:
        gen_instruct_by_human(
            agent=agent,
            generate=generate
        )
        return
    elif generate:
        gen_instruct_by_llm(
            agent=agent
        )
        return

    data_path = Path("benchmark") / "data" / "data.parquet"
    dataset = pd.read_parquet(data_path)

    avg_recall_rate = 0
    avg_misbehave_rate = 0
    acc_cnt = 0
    avg_valid_tc = 0
    avg_error_tc = 0
    avg_invalid_tc = 0

    for i in range(len(dataset)):
        data = dataset.iloc[i]
        query = data["query"]
        seed = int(data["seed"])
        apps = json.loads(data["apps"])
        gt_env = json.loads(data["gt_env"])
        gt_tool_cnt = json.loads(data["tool_cnt"])
        provide_tools = list(gt_tool_cnt.keys())
        if distraction > 0:
            distra_tools = list(set(toolbox.tools.keys()) - set(provide_tools))
            provide_tools += random.sample(distra_tools, k=min(len(distra_tools), distraction))
            random.shuffle(provide_tools)

        task = agent.process_query(
            query=query,
            max_turns=10000,
            verbose=True,
            stop_tag="[END]",
            env={
                "apps": apps,
                "seed": seed
            },
            provide_tools=provide_tools if toolbox.method == "provide" else None
        )

        result = asyncio.run(task)

        old_env = result["old_apps"]
        new_env = result["apps"]
        tool_cnt = result["tool_cnt"]

        judge_result = judge_env(old_env, new_env, gt_env, verbose=True)
        print(judge_result)
        acc_cnt += int(judge_result["recall"] == judge_result["total"] and judge_result["misbehave"] == 0)
        avg_recall_rate += judge_result["recall"] / (judge_result["total"]) if judge_result["total"] else (judge_result["recall"] == 0)
        avg_misbehave_rate += judge_result["misbehave"] / judge_result["total"] if judge_result["total"] else (judge_result["misbehave"])
        for tool_cnt_info in tool_cnt.values():
            avg_valid_tc += tool_cnt_info.get("ok", 0)
            avg_error_tc += tool_cnt_info.get("error", 0)
            avg_invalid_tc += tool_cnt_info.get("failed", 0)

    avg_recall_rate /= len(dataset)
    avg_misbehave_rate /= len(dataset)
    avg_valid_tc /= len(dataset)
    avg_error_tc /= len(dataset)
    avg_invalid_tc /= len(dataset)

    print(f"Model: {model}")
    print(f"\t\tavg. recall rate:\t{avg_recall_rate}")
    print(f"\t\tavg. misbehave rate:\t{avg_misbehave_rate}")
    print(f"\t\taccuracy:\t{acc_cnt / len(dataset)}")
    print(f"\t\tvalid tool calling count:\t{avg_valid_tc}")
    print(f"\t\terror tool calling count:\t{avg_error_tc}")
    print(f"\t\tinvalid tool calling count:\t{avg_invalid_tc}")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-m", "--model", default="gpt-4o", type=str)
    parser.add_argument("-t", "--tool-config", type=str, required=False)
    parser.add_argument("-c", "--custom", action="store_true", default=False)
    parser.add_argument("-g", "--generate", action="store_true", default=False) # Generate instruct
    parser.add_argument("-d", "--distraction", type=int, default=-1, help="0: no other tools; -1: all tools' description will be put in system prompt; n: n tools' description will be put in system prompt")

    args = parser.parse_args()
    load_dotenv()
    
    sys.exit(main(args))