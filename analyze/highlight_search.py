from pyecharts import options as opts
from pyecharts.charts import Line
from pyecharts.commons.utils import JsCode
import json
import os


def read_danmu_file(file_path):
    bullet_data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for item in data['danmaku']:
            time = float(item['time'])
            text = item['text']
            bullet_data.append((time, text))
    
    return bullet_data

def summarize_bullet_count_by_interval(bullet_data, interval=60):
    # 统计每个时间段内的弹幕数量
    time_periods = {}
    
    for time, _ in bullet_data:
        minute = int(time // interval)  # 按分钟划分
        time_periods[minute] = time_periods.get(minute, 0) + 1

    sorted_time_periods = sorted(time_periods.items())
    x_data = [str(minute) + "分钟" for minute, _ in sorted_time_periods]
    y_data = [count for _, count in sorted_time_periods]

    return x_data, y_data

def generate_bullet_count_chart(x_data, y_data, bv_number):
    background_color_js = (
        "new echarts.graphic.LinearGradient(0, 0, 0, 1, "
        "[{offset: 0, color: '#c86589'}, {offset: 1, color: '#06a7ff'}], false)"
    )
    area_color_js = (
        "new echarts.graphic.LinearGradient(0, 0, 0, 1, "
        "[{offset: 0, color: '#eb64fb'}, {offset: 1, color: '#3fbbff0d'}], false)"
    )
    
    line_chart = (
        Line(init_opts=opts.InitOpts(bg_color=JsCode(background_color_js)))
        .add_xaxis(xaxis_data=x_data)
        .add_yaxis(
            series_name="弹幕数量",
            y_axis=y_data,
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
                title=f"视频 {bv_number} 每分钟弹幕数量变化",
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

    return line_chart

def analyze_video(bv_number, video_path):
    # 为每个视频进行弹幕分析
    danmaku_file_path = os.path.join(video_path, 'danmaku.json')
    if not os.path.exists(danmaku_file_path):
        print(f"弹幕文件不存在：{danmaku_file_path}")
        return

    bullet_data = read_danmu_file(danmaku_file_path)

    interval = 10
    x_data, y_data = summarize_bullet_count_by_interval(bullet_data, interval)

    bullet_count_chart = generate_bullet_count_chart(x_data, y_data, bv_number)

    # 创建输出目录
    output_dir = os.path.join('crawled_data', bv_number, 'analyze')
    os.makedirs(output_dir, exist_ok=True)

    # 保存图表
    highlight_chart_path = os.path.join(output_dir, 'highlight_distribution.html')
    bullet_count_chart.render(highlight_chart_path)

    print(f"视频 {bv_number} 的分析结果已保存到 {highlight_chart_path}")

def main():
    crawled_data_dir = './crawled_data'
    
    for bv_number in os.listdir(crawled_data_dir):
        bv_path = os.path.join(crawled_data_dir, bv_number)
        if os.path.isdir(bv_path):
            analyze_video(bv_number, bv_path)

if __name__ == "__main__":
    main()
