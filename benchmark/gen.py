import sys
import os
from pathlib import Path
import json

WORK_DIR = Path('.').__str__()

if WORK_DIR not in sys.path:
    sys.path.append(WORK_DIR)


from client.agent import HumanAnnotator, AgentClient, Toolbox
from dotenv import load_dotenv
from argparse import ArgumentParser
import pandas as pd

import sys
import yaml
import asyncio

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
    tool_config_path = args.__getattribute__("tool_config")

    toolbox = parse_toolbox(tool_config_path) if tool_config_path else None

    llm = HumanAnnotator()
    agent = AgentClient(
        llm=llm,
        toolbox=toolbox,
        system_prompt=toolbox.get_system_prompt() if toolbox else ""
    )

    query = "Like Sharon Kennedy's last post in her moments. After you finish this task, output an '[END]' in the end."
    task = agent.process_query(
        query=query,
        max_turns=100,
        verbose=True,
        stop_tag="[END]",
        env={
            "apps": ["LightTalk"],
            "seed": 42
        }
    )

    result = asyncio.run(task)

    gt_env = result["apps"]

    data = [
        {
            "query": query,
            "seed": 42,
            "level": 1,
            "apps": ["LightTalk"],
            "rollout": result["output"],
            "gt_env": json.dumps(gt_env)
        }
    ]

    df = pd.DataFrame(data)
    data_path = Path("benchmark") / "data" / "data.parquet"
    if not os.path.exists(data_path):
        df.to_parquet(data_path)
    else:
        dfs = pd.read_parquet(data_path)
        dfs = pd.concat([dfs, df])
        dfs.to_parquet(data_path)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-t", "--tool-config", type=str, required=False)

    args = parser.parse_args()
    load_dotenv()
    
    sys.exit(main(args))