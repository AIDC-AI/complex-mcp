import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

# --- 数据定义 ---
x_labels = ["0", "50", "100", "All (300+)"]
x_values = [0, 50, 100, 150]

accuracy = {
    "GPT-4o": [31.91, 21.28, 17.02, 14.89],
    "DeepSeek-V3": [27.65, 23.40, 23.40, 19.15],
    "Gemini-3-Flash": [57.44, 55.31, 53.19, 55.31],
    "Claude-Opus-4": [51.06, 44.68, 40.42, 44.68]
}

completions = {
    "GPT-4o": [66.29, 45.60, 37.13, 29.01],
    "DeepSeek-V3": [52.64, 41.54, 40.04, 39.50],
    "Gemini-3-Flash": [86.42, 85.77, 85.29, 85.92],
    "Claude-Opus-4": [82.36, 81.45, 77.47, 77.19]
}

misbehave = {
    "GPT-4o": [5.56, 4.31, 4.05, 3.68],
    "DeepSeek-V3": [3.56, 4.11, 5.25, 3.05],
    "Gemini-3-Flash": [3.90, 4.20, 4.52, 4.12],
    "Claude-Opus-4": [4.09, 6.11, 5.27, 7.31]
}

# --- 绘图配置 ---
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11
# 使用更加学术的颜色面板
colors = {'GPT-4o': '#C44E52', 'DeepSeek-V3': '#4C72B0', 'Claude-Opus-4': '#55A868', 'Gemini-3-Flash': '#DD8452'}
markers = {'GPT-4o': 'o', 'DeepSeek-V3': 'D', 'Claude-Opus-4': 's', 'Gemini-3-Flash': '^'}

# --- 创建布局 (1行3列) ---
# 增加宽度以适应 1x3 布局
fig = plt.figure(figsize=(15, 4.5), dpi=300)
gs = gridspec.GridSpec(1, 3)

# 公用设置函数，减少代码重复
def setup_ax(ax, title, ylabel, ylim):
    ax.set_title(title, fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel("Number of Distractor Tools", fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_xticks(x_values)
    ax.set_xticklabels(x_labels)
    ax.set_ylim(ylim)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.tick_params(axis='both', which='major', labelsize=10)

# 1. 左侧：Accuracy
ax1 = fig.add_subplot(gs[0, 0])
for model in accuracy:
    ax1.plot(x_values, accuracy[model], marker=markers[model], color=colors[model], 
             label=model, linewidth=2, markersize=7)
setup_ax(ax1, r"(a) Success Rate $\uparrow$", "Accuracy (%)", (0, 85))

# 2. 中间：Completions
ax2 = fig.add_subplot(gs[0, 1])
for model in completions:
    ax2.plot(x_values, completions[model], marker=markers[model], color=colors[model], 
             linewidth=2, markersize=7)
setup_ax(ax2, r"(b) Completion Rate ($R_c$) $\uparrow$", "Rate (%)", (0, 105))

# 3. 右侧：Misbehave
ax3 = fig.add_subplot(gs[0, 2])
for model in misbehave:
    ax3.plot(x_values, misbehave[model], marker=markers[model], color=colors[model], 
             linewidth=2, markersize=7)
setup_ax(ax3, r"(c) Misbehaving Rate ($R_b$) $\downarrow$", "Rate (%)", (0, 10))

# --- 统一放置图例 ---
# 将图例放在三张图正上方中间位置
handles, labels = ax1.get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.08), 
           ncol=4, frameon=False, fontsize=12)

# 调整布局以适应图例
plt.tight_layout(rect=[0, 0, 1, 0.95])

# 保存
IMG_PATH = Path("imgs")
IMG_PATH.mkdir(exist_ok=True)
output_file = IMG_PATH / 'scaling_analysis_1x3.pdf'
plt.savefig(output_file, bbox_inches='tight')
print(f"Saved: {output_file}")
