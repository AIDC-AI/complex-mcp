import matplotlib.pyplot as plt
from pathlib import Path

# --- 数据定义 ---
labels = ['Prompt', 'Tool Feedback', 'LLM Generation']
counts = [29964.0, 1750.19, 901.2]

# 价格计算 (Costs) - 基于 Gemini-3-flash 比例: Input (1) / Output (6)
in_price = 1
out_price = 6
costs = [counts[0]*in_price, counts[1]*in_price, counts[2]*out_price]

# --- 绘图风格设置 ---
colors = ['#5B84B1', '#7FB069', '#E6AA68'] 
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11

# 创建画布：1行2列
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5), dpi=300)

def draw_donut(ax, data, title):
    # 绘制饼图
    # 获取 wedges 用于后续生成图例
    wedges, texts, autotexts = ax.pie(
        data, 
        autopct='%1.1f%%', 
        startangle=140, 
        colors=colors, 
        pctdistance=0.75, 
        # 使用 labels=None 确保内部不生成乱七八糟的文字，由统一图例管理
        explode=[0.03]*len(data)
    )
    
    # 将百分比字体设为深灰色，加粗
    plt.setp(autotexts, size=10, weight="bold", color="#333333")
    
    # 变成环形图 (Donut)
    centre_circle = plt.Circle((0,0), 0.60, fc='white')
    ax.add_artist(centre_circle)
    
    # 设置子图标题
    ax.set_title(title, fontsize=13, fontweight='bold', pad=10)
    
    return wedges # 返回句柄

# 绘图并获取句柄
wedges1 = draw_donut(ax1, counts, '(a) Token Count Distribution')
wedges2 = draw_donut(ax2, costs, '(b) Estimated Cost Distribution')

# --- 共享图例 ---
# 使用返回的 wedges1 作为句柄，labels 作为标签
fig.legend(
    handles=wedges1, 
    labels=labels,
    title="Token Categories",
    loc="lower center", 
    bbox_to_anchor=(0.5, 0.02),
    ncol=3, 
    frameon=False,
    fontsize=11
)

# 调整整体布局
# rect=[左, 下, 右, 上] 这里的 0.12 是为了给底部的 legend 留出足够的空间
plt.tight_layout(rect=[0, 0.12, 1, 0.95])

# 保存路径
IMG_PATH = Path("imgs")
IMG_PATH.mkdir(exist_ok=True)
output_file = IMG_PATH / 'token_analysis_combined.pdf'

plt.savefig(output_file, bbox_inches='tight')
print(f"Saved: {output_file}")
