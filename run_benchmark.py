from client.agent import OpenAIBackend, AgentClient, Toolbox
from benchmark.judge import judge_env
from dotenv import load_dotenv
from argparse import ArgumentParser
from pathlib import Path
import json

import sys
import yaml
import asyncio

import pandas as pd

def parse_toolbox(tool_config_path: str | Path):
    config = {}
    with open(tool_config_path) as f:
        data = yaml.safe_load(f)
        config["servers"] = data["servers"]

    toolbox = Toolbox()
    for server in config["servers"]:
        if not server["use"]: continue
        server_args = {
            "server_name": server["name"],
            "server_url": server["url"],
            "desc_path": server["desc"],
            "use_sandbox": server.get("use_sandbox", False)
        }
        toolbox.register_server(**server_args)
    
    return toolbox

def main(args):
    model = args.__getattribute__("model")
    tool_config_path = args.__getattribute__("tool_config")
    custom = args.__getattribute__("custom")

    toolbox = parse_toolbox(tool_config_path) if tool_config_path else None

    llm = OpenAIBackend(model=model)
    agent = AgentClient(
        llm=llm,
        toolbox=toolbox,
        system_prompt=toolbox.get_system_prompt() if toolbox else ""
    )

    if custom:
        apps = [app for app in toolbox.servers if app in {"LightTalk", "LightShop"}]

        seed = int(input("> seed: "))
        query = f"{input('> instruct: ')}\nAfter you finish the task, output an [END] in the final."

        task = agent.process_query(
            query=query,
            max_turns=100,
            verbose=True,
            stop_tag="[END]",
            env={
                "apps": apps,
                "seed": seed
            }
        )
        
        asyncio.run(task)

        return
        

    data_path = Path("benchmark") / "data" / "data.parquet"
    dataset = pd.read_parquet(data_path)

    avg_recall_rate = 0
    avg_misbehave_rate = 0

    for i in range(len(dataset)):
        data = dataset.iloc[i]
        query = data["query"]
        seed = int(data["seed"])
        apps = data["apps"]
        gt_env = json.loads(data["gt_env"])

        task = agent.process_query(
            query=query,
            max_turns=100,
            verbose=True,
            stop_tag="[END]",
            env={
                "apps": apps,
                "seed": seed
            }
        )

        result = asyncio.run(task)

        old_env = result["old_apps"]
        new_env = result["apps"]

        judge_result = judge_env(old_env, new_env, gt_env)
        print(judge_result)
        avg_recall_rate += judge_result["recall"] / judge_result["total"]
        avg_misbehave_rate += judge_result["misbehave"] / judge_result["total"]

    avg_recall_rate /= len(dataset)
    avg_misbehave_rate /= len(dataset)

    print(f"Model: {model}")
    print(f"\t\tavg. recall rate:\t{avg_recall_rate}")
    print(f"\t\tavg. misbehave rate:\t{avg_misbehave_rate}")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-m", "--model", default="gpt-4o", type=str)
    parser.add_argument("-t", "--tool-config", type=str, required=False)
    parser.add_argument("-c", "--custom", action="store_true", default=False)

    args = parser.parse_args()
    load_dotenv()
    
    sys.exit(main(args))