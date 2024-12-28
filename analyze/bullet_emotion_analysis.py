
# 分析弹幕情感并生成分布表格

import os
import json
from snownlp import SnowNLP
from pyecharts import options as opts
from pyecharts.charts import Bar, Pie, Page

def read_video_info(file_path):
    # 读取视频信息文件
    with open(file_path, 'r', encoding='utf-8') as file:
        video_info = json.load(file)
    return video_info

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

def analyze_video(bv_number, video_path):
    # 为每个视频进行情感分析
    danmaku_file_path = os.path.join(video_path, 'danmaku.json')
    if not os.path.exists(danmaku_file_path):
        print(f"弹幕文件不存在：{danmaku_file_path}")
        return
    
    danmakus = read_danmu_file(danmaku_file_path)
    emotions = analyze_emotion(danmakus)
    average_emotion = sum(emotions) / len(emotions) if emotions else 0

    print(f"视频 {bv_number} 的平均情感分数是: {average_emotion:.2f}")

    # 保存结果到文件
    output_dir = os.path.join('analysis_data', bv_number)
    os.makedirs(output_dir, exist_ok=True)

    # 保存情感分析结果到文件
    result_file_path = os.path.join(output_dir, 'emotion_analysis_results.txt')
    with open(result_file_path, 'w', encoding='utf-8') as file:
        file.write(f"视频 {bv_number} 所有弹幕的平均情感分数是: {average_emotion:.2f}\n")
        file.write("\n弹幕情感分数如下:\n")
        for idx, emotion in enumerate(emotions):
            file.write(f"弹幕 {idx + 1}: {emotion:.2f}\n")

    # 生成情感分布图
    emotion_bar_chart = generate_emotion_bar_chart(emotions)
    emotion_pie_chart = generate_emotion_pie_chart(emotions)

    # 使用Page将多个图表合并到同一个HTML页面
    page = Page()
    page.add(emotion_bar_chart)
    page.add(emotion_pie_chart)

    emotion_chart_path = os.path.join(output_dir, 'emotion_distribution.html')
    page.render(emotion_chart_path)

    print(f"视频 {bv_number} 的分析结果已保存到 {emotion_chart_path} 和 {result_file_path}")

def get_top_videos(crawled_data_dir, top_n=10):
    # 获取播放量最高的 n 个视频
    video_view_counts = []
    for bv_number in os.listdir(crawled_data_dir):
        bv_path = os.path.join(crawled_data_dir, bv_number)
        if os.path.isdir(bv_path):
            video_info_file_path = os.path.join(bv_path, 'video_info.json')
            if os.path.exists(video_info_file_path):
                video_info = read_video_info(video_info_file_path)
                view_count = video_info.get('view', 0)
                video_view_counts.append((bv_number, view_count))

    # 按照播放量降序排序并选择前 n 个视频
    top_videos = sorted(video_view_counts, key=lambda x: x[1], reverse=True)[:top_n]
    return [video[0] for video in top_videos]

def main():
    crawled_data_dir = './crawled_data'

    top_videos = get_top_videos(crawled_data_dir, top_n=10)
    
    for bv_number in top_videos:
        bv_path = os.path.join(crawled_data_dir, bv_number)
        if os.path.isdir(bv_path):
            analyze_video(bv_number, bv_path)

if __name__ == "__main__":
    main()
