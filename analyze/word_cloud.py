import pandas as pd
from pyecharts.charts import WordCloud, Bar, Page
from pyecharts import options as opts


def generate_word_freq_bar(word_freq, n=10):
    bar = Bar()
    bar.add_xaxis([w for w, _ in word_freq[0:n]])
    bar.add_yaxis("", [c for _, c in word_freq[0:n]])
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="词频柱状图"),
        xaxis_opts=opts.AxisOpts(name=""),
        yaxis_opts=opts.AxisOpts(name="频次")
    )
    return bar


def create_word_cloud(word_freq_file, word_cloud_file, n=80):
    # 指定列名
    column_names = ['SerialNumber', 'Content', 'Frequency']

    # 步骤2：读取CSV文件，并指定列名
    df = pd.read_csv(word_freq_file, header=None, names=column_names)

    # 步骤3：筛选top数据
    top = df.iloc[0:n]

    # 步骤4：生成词云数据
    # 确保频率列中的数据是有效的整数
    word_freq = []
    for index, row in top.iterrows():
        content, frequency = row['Content'], str(row['Frequency'])  # 将频率转换为字符串
        if frequency.isdigit():  # 检查字符串是否只包含数字
            word_freq.append((content, int(frequency)))  # 添加到词云数据列表
    
    word_freq_bar = generate_word_freq_bar(word_freq)

    # 步骤5：使用pyecharts生成词云图
    word_cloud = (
        WordCloud()
        .add("", word_freq, word_size_range=[20, 100], shape='circle')
        .set_global_opts(title_opts=opts.TitleOpts(title="词云"))
    )

    # 步骤6：渲染和保存词云图
    page = Page().add(word_freq_bar).add(word_cloud)
    page.render(word_cloud_file)  # 保存为HTML文件
