import json
import os
import datetime
from collections import defaultdict
import pyecharts.options as opts
from pyecharts.charts import Line
from pyecharts.globals import JsCode

def read_video_info(file_path):
    # 读取视频信息文件
    with open(file_path, 'r', encoding='utf-8') as file:
        video_info = json.load(file)
    return video_info

def extract_comments(bv_path):
    # 提取视频下所有评论的时间戳
    comments = []
    comments_file_path = os.path.join(bv_path, 'comments.json')
    
    if os.path.exists(comments_file_path):
        with open(comments_file_path, 'r', encoding='utf-8') as file:
            comments_data = json.load(file)
            for comment in comments_data.get('comments', []):
                # 提取评论及其回复的时间戳
                comments.append(comment['user']['time'])
                for reply in comment.get('replies', []):
                    comments.append(reply['user']['time'])
    
    return comments

def calculate_daily_activity(comments):
    # 计算每日活力（评论数）
    daily_activity = defaultdict(int)
    for timestamp in comments:
        date = datetime.datetime.fromtimestamp(timestamp).date()
        daily_activity[date] += 1
    
    return daily_activity

def generate_activity_line_chart(daily_activity, bv_number):
    # 生成每日评论数（活力）折线图
    dates = list(daily_activity.keys())
    activities = list(daily_activity.values())

    # 定义渐变色
    background_color_js = (
        "new echarts.graphic.LinearGradient(0, 0, 0, 1, "
        "[{offset: 0, color: '#c86589'}, {offset: 1, color: '#06a7ff'}], false)"
    )
    area_color_js = (
        "new echarts.graphic.LinearGradient(0, 0, 0, 1, "
        "[{offset: 0, color: '#eb64fb'}, {offset: 1, color: '#3fbbff0d'}], false)"
    )
    
    # 创建折线图
    line_chart = (
        Line(init_opts=opts.InitOpts(bg_color=JsCode(background_color_js)))
        .add_xaxis(xaxis_data=[str(date) for date in dates])
        .add_yaxis(
            series_name="评论数（活力）",
            y_axis=activities,
            is_smooth=True,
            symbol="circle",
            symbol_size=6,
            linestyle_opts=opts.LineStyleOpts(color="#fff"),
            label_opts=opts.LabelOpts(is_show=True, position="top", color="white"),
            itemstyle_opts=opts.ItemStyleOpts(
                color="red", border_color="#fff", border_width=3
            ),
            tooltip_opts=opts.TooltipOpts(is_show=True),
            areastyle_opts=opts.AreaStyleOpts(
                color=JsCode(area_color_js), opacity=1),
            markpoint_opts=opts.MarkPointOpts(
                data=[opts.MarkPointItem(type_="max")])
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=f"视频 {bv_number} 每日活力折线图",
                pos_bottom="90%",
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(
                    color="#fff", font_size=16),
            ),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                boundary_gap=False,
                axislabel_opts=opts.LabelOpts(margin=30, color="#ffffff63"),
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(width=2, color="#fff")
                ),
                axistick_opts=opts.AxisTickOpts(
                    is_show=True,
                    length=25,
                    linestyle_opts=opts.LineStyleOpts(color="#ffffff1f"),
                ),
                splitline_opts=opts.SplitLineOpts(
                    is_show=True, linestyle_opts=opts.LineStyleOpts(color="#ffffff1f")
                )
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                position="left",
                axislabel_opts=opts.LabelOpts(margin=20, color="#ffffff63"),
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(width=2, color="#fff")
                ),
                axistick_opts=opts.AxisTickOpts(
                    is_show=True,
                    length=15,
                    linestyle_opts=opts.LineStyleOpts(color="#ffffff1f"),
                ),
                splitline_opts=opts.SplitLineOpts(
                    is_show=True, linestyle_opts=opts.LineStyleOpts(color="#ffffff1f")
                ),
            ),
            legend_opts=opts.LegendOpts(is_show=False),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="line")
        )
    )

    # 生成 HTML 文件
    output_dir = os.path.join('crawled_data', bv_number, 'analyze')
    os.makedirs(output_dir, exist_ok=True)

    line_chart_path = os.path.join(output_dir, 'daily_activity.html')
    line_chart.render(line_chart_path)
    print(f"视频 {bv_number} 的每日活力折线图已保存到 {line_chart_path}")

def analyze_video_activity(bv_number, bv_path):
    # 提取评论并计算每日活力
    comments = extract_comments(bv_path)
    daily_activity = calculate_daily_activity(comments)
    
    # 从视频信息中获取播放量和发布时间
    video_info_file_path = os.path.join(bv_path, 'video_info.json')
    video_info = read_video_info(video_info_file_path)
    pubdate = video_info.get('pubdate')
    view_count = video_info.get('view')

    # 将时间戳转换为日期
    pubdate = datetime.datetime.fromtimestamp(pubdate).date() if pubdate else None
    
    # 生成视频活力折线图
    generate_activity_line_chart(daily_activity, bv_number)

def main():
    crawled_data_dir = './crawled_data'

    for bv_number in os.listdir(crawled_data_dir):
        bv_path = os.path.join(crawled_data_dir, bv_number)
        if os.path.isdir(bv_path):
            analyze_video_activity(bv_number, bv_path)

if __name__ == "__main__":
    main()
