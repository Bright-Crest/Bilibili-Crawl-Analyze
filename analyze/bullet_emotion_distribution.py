
# 分析弹幕情感并生成分布表格

from pyecharts import options as opts
from pyecharts.charts import Bar, Pie, Page
from snownlp import SnowNLP
import json
import webbrowser
import os


def read_danmu_file(file_path):
    # 读取弹幕内容文件text字段

    bullet_text = []
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for item in data['danmaku']:
            bullet_text.append(item['text']) 
    
    return bullet_text


def analyze_emotion(danmakus):
    # 分析弹幕的情感
    emotions = [SnowNLP(danmu).sentiments for danmu in danmakus]
    return emotions


def generate_emotion_bar_chart(emotions):
    # 生成情感分布柱状图
    emotion_bins = [0, 0.2, 0.4, 0.6, 0.8, 1]
    emotion_labels = ['非常负面', '负面', '中性', '正面', '非常正面']

    # 计算每个区间的频次
    emotion_counts = [0] * (len(emotion_bins) - 1)
    for emotion in emotions:
        for i in range(len(emotion_bins) - 1):
            if emotion_bins[i] <= emotion < emotion_bins[i + 1]:
                emotion_counts[i] += 1
                break

    bar = Bar()
    bar.add_xaxis(emotion_labels)
    bar.add_yaxis('情感分布', emotion_counts)
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="弹幕情感分布柱状图"),
        xaxis_opts=opts.AxisOpts(name="情感倾向"),
        yaxis_opts=opts.AxisOpts(name="弹幕数量")
    )

    return bar

def generate_emotion_pie_chart(emotions):
    # 生成情感分布饼状图
    emotion_bins = [0, 0.2, 0.4, 0.6, 0.8, 1]
    emotion_labels = ['非常负面', '负面', '中性', '正面', '非常正面']

    # 计算每个区间的频次
    emotion_counts = [0] * (len(emotion_bins) - 1)
    for emotion in emotions:
        for i in range(len(emotion_bins) - 1):
            if emotion_bins[i] <= emotion < emotion_bins[i + 1]:
                emotion_counts[i] += 1
                break

    pie = Pie()
    pie.add("情感分布", [list(z) for z in zip(emotion_labels, emotion_counts)])
    pie.set_global_opts(
        title_opts=opts.TitleOpts(title="弹幕情感分布饼状图")
    )
    pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {d}%"))
    
    return pie

def main():
    input_file_path = './danmaku.json'
    emotion_chart_path = 'emotion_distribution.html'

    # 读取弹幕文本内容
    danmakus = read_danmu_file(input_file_path)

    # 情感分析
    emotions = analyze_emotion(danmakus)

    # 生成情感分布图
    emotion_bar_chart = generate_emotion_bar_chart(emotions)
    emotion_pie_chart = generate_emotion_pie_chart(emotions)

    # 使用Page将多个图表合并到同一个HTML页面
    page = Page()
    page.add(emotion_bar_chart)
    page.add(emotion_pie_chart)

    page.render(emotion_chart_path)

    # 自动打开生成的HTML文件
    file_url = os.path.abspath(emotion_chart_path)
    webbrowser.open(f'file://{file_url}')


if __name__ == "__main__":
    main()