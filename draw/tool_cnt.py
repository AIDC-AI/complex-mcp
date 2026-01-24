import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

# --- 数据定义 ---
x_labels = ["0", "50", "100", "All (300+)"]
x_values = [0, 50, 100, 150]

accuracy = {
    "GPT-4o": [31.91, 21.28, 17.02, 14.89],
    "DeepSeek-V3": [27.65, 23.40, 23.40, 19.15],
    "Gemini-3-Flash": [57.44, 55.31, 53.19, 59.57],
    "Claude-Opus-4": [51.06, 44.68, 40.42, 44.68]
}

completions = {
    "GPT-4o": [66.29, 45.60, 37.13, 29.01],
    "DeepSeek-V3": [52.64, 41.54, 40.04, 39.50],
    "Gemini-3-Flash": [86.42, 85.77, 85.29, 86.33],
    "Claude-Opus-4": [82.36, 81.45, 77.47, 77.19]
}

misbehave = {
    "GPT-4o": [5.56, 4.31, 4.05, 3.68],
    "DeepSeek-V3": [3.56, 4.11, 5.25, 3.05],
    "Gemini-3-Flash": [3.90, 4.20, 4.52, 3.57],
    "Claude-Opus-4": [4.09, 6.11, 5.27, 7.31]
}

# --- 绘图配置 ---
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
colors = {'GPT-4o': '#C44E52', 'DeepSeek-V3': '#4C72B0', 'Claude-Opus-4': '#55A868', 'Gemini-3-Flash': '#DD8452'}
markers = {'GPT-4o': 'o', 'DeepSeek-V3': 'D', 'Claude-Opus-4': 's', 'Gemini-3-Flash': '^'}

# --- 创建布局 ---
fig = plt.figure(figsize=(10, 8), dpi=300)
gs = gridspec.GridSpec(2, 2, height_ratios=[1, 1])

# 1. 顶部：Accuracy
ax_top = fig.add_subplot(gs[0, :])
lines = []
for model in accuracy:
    line, = ax_top.plot(x_values, accuracy[model], marker=markers[model], color=colors[model], 
                        label=model, linewidth=2, markersize=8)
    lines.append(line)

ax_top.set_title(r"(a) Success Rate $\uparrow$", fontsize=12, fontweight='bold', pad=35) # 增加 pad 给图例留位
ax_top.set_xlabel("Number of Distractor Tools")
ax_top.set_ylabel("Accuracy (%)")
ax_top.set_xticks(x_values)
ax_top.set_xticklabels(x_labels)
ax_top.set_ylim(0, 85) # 稍微调高 y 轴上限，防止数据碰到顶部的图例
ax_top.grid(True, linestyle='--', alpha=0.6)

# 将图例移动到子图上方，ncol=2 表示横向排列
ax_top.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=4, frameon=False, fontsize=11)

# 2. 左下：Completions
ax_left = fig.add_subplot(gs[1, 0])
for model in completions:
    ax_left.plot(x_values, completions[model], marker=markers[model], color=colors[model], 
                 linewidth=1.5, markersize=6)
ax_left.set_title(r"(b) Completion Rate ($R_c$) $\uparrow$", fontsize=12, fontweight='bold')
ax_left.set_xlabel("Number of Distractor Tools")
ax_left.set_ylabel("Rate (%)")
ax_left.set_xticks(x_values)
ax_left.set_xticklabels(x_labels)
ax_left.set_ylim(0, 105)
ax_left.grid(True, linestyle='--', alpha=0.6)

# 3. 右下：Misbehave
ax_right = fig.add_subplot(gs[1, 1])
for model in misbehave:
    ax_right.plot(x_values, misbehave[model], marker=markers[model], color=colors[model], 
                  linewidth=1.5, markersize=6)
ax_right.set_title(r"(c) Misbehaving Rate ($R_b$) $\downarrow$", fontsize=12, fontweight='bold')
ax_right.set_xlabel("Number of Distractor Tools")
ax_right.set_ylabel("Rate (%)")
ax_right.set_xticks(x_values)
ax_right.set_xticklabels(x_labels)
ax_right.set_ylim(0, 10) # 针对 Rb 指标较小的特点微调
ax_right.grid(True, linestyle='--', alpha=0.6)

# 调整布局
plt.tight_layout()

# 保存
IMG_PATH = Path("imgs")
IMG_PATH.mkdir(exist_ok=True)
output_file = IMG_PATH / 'scaling_analysis.pdf'
plt.savefig(output_file, bbox_inches='tight')
print(f"Saved: {output_file}")
