import json
import os
import datetime
import numpy as np
import scipy.stats as stats
import pandas as pd
from pyecharts.charts import Scatter
from pyecharts import options as opts
import webbrowser

def read_video_info(file_path):
    # 读取视频信息文件
    with open(file_path, 'r', encoding='utf-8') as file:
        video_info = json.load(file)
    return video_info

def collect_video_data(crawled_data_dir):
    # 收集所有视频的播放量与发布时间
    all_pubdates = []
    all_views = []
    bv_numbers = []

    for bv_number in os.listdir(crawled_data_dir):
        bv_path = os.path.join(crawled_data_dir, bv_number)
        if os.path.isdir(bv_path):
            video_info_file_path = os.path.join(bv_path, 'video_info.json')
            if os.path.exists(video_info_file_path):
                video_info = read_video_info(video_info_file_path)
                pubdate = video_info.get('pubdate')
                view_count = video_info.get('view')
                if pubdate and view_count is not None:
                    all_pubdates.append(pubdate)
                    all_views.append(view_count)
                    bv_numbers.append(bv_number)
    
    return bv_numbers, all_pubdates, all_views

def analyze_view_time_relation(pubdates, views):
    # 计算皮尔逊相关系数
    correlation, _ = stats.pearsonr(np.array(pubdates).astype(float), np.array(views).astype(float))
    return correlation

def generate_scatter_chart(pubdates, views, correlation):
    # 转换时间戳为日期
    pubdates = [datetime.datetime.fromtimestamp(pubdate) for pubdate in pubdates]

    # 生成散点图
    scatter = Scatter()
    scatter.add_xaxis(pubdates)
    scatter.add_yaxis("播放量", views, 
                       symbol_size=8,  # 增加点的大小
                       itemstyle_opts=opts.ItemStyleOpts(color='steelblue'),  # 设置点的颜色
                       label_opts=opts.LabelOpts(is_show=False))  # 隐藏标签
    
    scatter.set_global_opts(
        title_opts=opts.TitleOpts(title=f"播放量与发布时间关系 (相关性: {correlation:.2f})"),
        xaxis_opts=opts.AxisOpts(type_="time", name="发布时间"),
        yaxis_opts=opts.AxisOpts(name="播放量"),
        toolbox_opts=opts.ToolboxOpts(is_show=True),  # 显示工具栏
        visualmap_opts=opts.VisualMapOpts(
            max_=max(views),
            pos_top='40%',
            pos_right='0%',
            is_show=True
        )
    )
    
    return scatter

def main():
    crawled_data_dir = './crawled_data'

    # 收集所有视频的播放量和发布时间
    bv_numbers, all_pubdates, all_views = collect_video_data(crawled_data_dir)

    # 计算皮尔逊相关系数
    correlation = analyze_view_time_relation(all_pubdates, all_views)
    print(f"所有视频的播放量与发布时间之间的皮尔逊相关系数: {correlation:.2f}")

    # 生成一个大表格
    video_data = pd.DataFrame({
        'BV号': bv_numbers,
        '发布时间': [datetime.datetime.fromtimestamp(pubdate) for pubdate in all_pubdates],
        '播放量': all_views
    })

    # 增加字体大小与列宽，保存到CSV文件
    video_data.to_csv('./view_time_relation.csv', index=False)
    print("所有视频的播放量与发布时间的数据已保存到 'view_time_relation.csv'")

    # 显示表格的一部分（更好地查看数据）
    print(video_data.head())

    # 生成并保存散点图
    scatter_chart = generate_scatter_chart(all_pubdates, all_views, correlation)
    scatter_chart_path = './view_time_relation.html'
    scatter_chart.render(scatter_chart_path)

    # 自动打开生成的散点图
    webbrowser.open(f'file://{os.path.abspath(scatter_chart_path)}')

if __name__ == "__main__":
    main()
