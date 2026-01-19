from pathlib import Path
from matplotlib import pyplot as plt
import pandas as pd
import json
from collections import defaultdict
import numpy as np

# 确保输出目录存在
img_dir = Path("imgs")
img_dir.mkdir(exist_ok=True)

# 读取数据
data_path = Path("benchmark") / "data" / "data.parquet"
df = pd.read_parquet(data_path)

tool_cnt_dict = defaultdict(int)
tool_calling_cnt_dict = defaultdict(int)

for i in range(len(df)):
    item = df.iloc[i]
    tool_cnt_info = json.loads(item["tool_cnt"])

    tool_cnt = len(tool_cnt_info.keys())
    tool_calling_cnt = 0
    for tc_details in tool_cnt_info.values():
        for tc in tc_details.values():
            tool_calling_cnt += tc
    
    tool_cnt_dict[tool_cnt] += 1
    tool_calling_cnt_dict[tool_calling_cnt] += 1

total_samples = len(df)

def get_binned_proportions(freq_dict, bin_width=3):
    if not freq_dict:
        return [], []
    keys = np.array(list(freq_dict.keys()))
    values = np.array(list(freq_dict.values()))
    min_val = keys.min()
    max_val = keys.max()
    bins = np.arange(min_val, max_val + bin_width, bin_width)
    counts, _ = np.histogram(keys, bins=bins, weights=values)
    proportions = counts / total_samples
    labels = bins[:-1].astype(int)
    return labels, proportions

x_tool, y_tool = get_binned_proportions(tool_cnt_dict, bin_width=3)
x_calling, y_calling = get_binned_proportions(tool_calling_cnt_dict, bin_width=3)

# 公共绘图参数（适合论文）
figsize_single = (3.8, 2.5)  # 宽 x 高（英寸）
params = {
    'font.size': 9,
    'axes.labelsize': 9,
    'axes.titlesize': 10,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
}
plt.rcParams.update(params)

# --- 图1：工具种类数量分布 ---
fig, ax = plt.subplots(figsize=figsize_single)
ax.bar(x_tool, y_tool, width=2.7, color='skyblue', edgecolor='black', align='edge')
ax.set_xlabel('Number of tools per sample')
ax.set_ylabel('Proportion')
ax.set_title('Tool count distribution')
ax.set_xticks(x_tool)
fig.tight_layout()
fig.savefig(img_dir / "tool_count_distribution.pdf", bbox_inches='tight', dpi=300)
fig.savefig(img_dir / "tool_count_distribution.png", bbox_inches='tight', dpi=300)
plt.close(fig)

# --- 图2：工具调用总次数分布 ---
fig, ax = plt.subplots(figsize=figsize_single)
ax.bar(x_calling, y_calling, width=2.7, color='lightgreen', edgecolor='black', align='edge')
ax.set_xlabel('Total tool calls per sample')
ax.set_ylabel('Proportion')
ax.set_title('Tool calling distribution')
# 如果 x 轴太密集，自动稀疏化
if len(x_calling) > 15:
    step = max(1, len(x_calling) // 8)
    ax.set_xticks(x_calling[::step])
else:
    ax.set_xticks(x_calling)
fig.tight_layout()
fig.savefig(img_dir / "tool_calling_distribution.pdf", bbox_inches='tight', dpi=300)
fig.savefig(img_dir / "tool_calling_distribution.png", bbox_inches='tight', dpi=300)
plt.close(fig)

print(f"✅ Saved figures to {img_dir}/")
