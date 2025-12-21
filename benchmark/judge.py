from typing import List, Dict, Any

def exact_match(x: str, y: str):
    return x == y

exclude_keys = [
    "timestamp"
]

eq_methods = {}

def judge_env(
    old_env: Dict[str, Any],
    new_env: Dict[str, Any],
    gt_env: Dict[str, Any]
) -> Dict[str, int]:
    total = 0
    recall = 0
    misbehave = 0

    def dfs(
        old_env_item: Dict[str, Any] | None,
        new_env_item: Dict[str, Any] | None,
        gt_env_item: Dict[str, Any]
    ):
        nonlocal total, recall, misbehave
        for key in gt_env_item:
            if key in exclude_keys:
                continue
            old_val = old_env_item.get(key) if old_env_item else None
            new_val = new_env_item.get(key) if new_env_item else None
            gt_val = gt_env_item[key]
            if isinstance(gt_val, dict):
                dfs(
                    old_val,
                    new_val,
                    gt_val
                )
                continue
            __eq_func = eq_methods.get(key, exact_match)
            if __eq_func(gt_val, old_val):
                # The values which should not be changed
                if not __eq_func(new_val, old_val):
                    misbehave += 1
            else:
                # The values which should be changed
                total += 1
                if __eq_func(new_val, gt_val):
                    recall += 1
    
    dfs(old_env, new_env, gt_env)
        
    return {
        "total": total,
        "recall": recall,
        "misbehave": misbehave
    }


if __name__ == "__main__":
    old_env = {
        "apple": {
            "price": 100,
            "count": 20
        },
        "banana": {
            "price": 120,
            "count": 15
        }
    }

    gt_env = {
        "apple": {
            "price": 110,
            "count": 20
        },
        "banana": {
            "price": 100,
            "count": 15
        }
    }

    new_env = {
        "apple": {
            "price": 110,
            "count": 20
        },
        "banana": {
            "price": 120,
            "count": 10
        }
    }

    result = judge_env(old_env, new_env, gt_env)
    print(result)