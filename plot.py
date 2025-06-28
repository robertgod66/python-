import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 配置中文显示和图表样式
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体显示中文
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题
plt.style.use('ggplot')                       # 使用ggplot风格

# 读取数据（根据实际路径修改）
df = pd.read_excel('豆瓣电影Top250.xlsx')


# ======================
# 1. 年份分布折线图
# ======================
# 对年份列进行排序
sorted_df = df.sort_values(by='年份')

# 统计每个年份的电影数量
year_counts = sorted_df['年份'].value_counts().sort_index()



# 绘制折线图
plt.figure(figsize=(10, 6))
plt.plot(year_counts.index.astype(str), year_counts.values)

# 添加标题和标签
plt.title('豆瓣电影Top250年份分布折线图')
plt.xlabel('年份')
plt.xticks(rotation=45)
plt.ylabel('电影数量')

# 显示图表
plt.show()
# ======================
# 2. 类型分布饼图（合并<3%的类型）
# ======================
# 数据预处理
# 拆分复合类型并展开
split_types = (df['类型'].str.split(' ', expand=True)  # 按空格拆分类型
              .stack()                               # 展开为多行
              .str.strip()                           # 去除前后空格
              .value_counts())                       # 统计类型频次

# 计算百分比
total = split_types.sum()
percentages = (split_types / total * 100).round(1)

# 合并小类
threshold = 3  # 3%阈值
main_types = percentages[percentages >= threshold]
other_percent = percentages[percentages < threshold].sum()
final_data = main_types._append(pd.Series({'其他': other_percent}))

# 创建画布
plt.figure(2,figsize=(30, 5))
plt.sca(plt.subplot(1, 2, 1))
# 绘制饼图
wedges, texts, autotexts = plt.pie(
    final_data.values,
    labels=final_data.index,
    autopct='%1.1f%%',
    startangle=90,
    counterclock=False,
    colors=plt.cm.Paired.colors,
    pctdistance=0.85,
    textprops={'fontsize': 10}
)

# 添加中心空白（甜甜圈效果）
centre_circle = plt.Circle((0,0), 0.70, fc='white')
plt.gca().add_artist(centre_circle)

# 添加图例
plt.legend(wedges,
           final_data.index,
           title="电影类型",
           loc="center left",
           bbox_to_anchor=(1, 0, 0.5, 1))

# 图表装饰
plt.title('电影类型分布', fontsize=14, pad=20)
plt.tight_layout()




# 处理国家/地区列，将多国家/地区的电影进行拆分
countries = []
for region in df['国家/地区']:
    if isinstance(region, str):
        sub_regions = region.split(' ')
        countries.extend(sub_regions)

# 统计每个国家/地区出现的次数
country_counts = pd.Series(countries).value_counts()

# 绘制柱状图
plt.sca(plt.subplot(1, 2, 2))
country_counts.plot(kind='bar')

# 添加标题和标签
plt.title('豆瓣电影Top250国家/地区分布')
plt.xlabel('国家/地区')
plt.ylabel('电影数量')

# 显示图表
plt.show()