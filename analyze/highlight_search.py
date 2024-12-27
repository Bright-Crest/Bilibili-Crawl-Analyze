import csv
from collections import defaultdict
from pyecharts import options as opts
from pyecharts.charts import Bar
import webbrowser
import os

def read_danmu_file(file_path):
    bullet_data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)

        for row in csv_reader:
            time, type, color, text = row
            bullet_data.append((float(time), text))
    
    return bullet_data

def summarize_bullet_count_by_interval(bullet_data, interval=10):
    # 统计每个时间段内的弹幕数量
    time_periods = defaultdict(int)

    for time, text in bullet_data:
        time_slot = int(time // interval) * interval
        time_periods[time_slot] += 1
    
    # 将统计结果按时间顺序排序
    sorted_time_periods = sorted(time_periods.items())

    # 获取弹幕数量最多的时间段
    max_bullet_count = max(time_periods.values())
    high_light_time = [period for period, count in time_periods.items() if count == max_bullet_count]

    return sorted_time_periods, max_bullet_count, high_light_time

def generate_bullet_count_chart(sorted_time_periods, high_light_time):
    # 生成柱状图
    time_slots = [f"{start_time:.2f}-{start_time+2:.2f}s" for start_time, _ in sorted_time_periods]
    bullet_counts = [count for _, count in sorted_time_periods]

    bar = Bar()
    bar.add_xaxis(time_slots)
    bar.add_yaxis("弹幕数量", bullet_counts, itemstyle_opts=opts.ItemStyleOpts(color='steelblue'))

    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="每个时间段内的弹幕数量"),
        xaxis_opts=opts.AxisOpts(name="时间段"),
        yaxis_opts=opts.AxisOpts(name="弹幕数量")
    )

    return bar

def generate_highlight_info(high_light_time, max_bullet_count):
    # 生成高光时刻的文字信息
    return f'<b1><b style="color:red;">高光时刻：</b> 时间段: {high_light_time[0]:.2f}-{high_light_time[0]+2:.2f}秒<br><br><b>弹幕数量</b>: {max_bullet_count} 条。</b1>'

def main():
    input_file_path = './danmus.csv'
    bullet_data = read_danmu_file(input_file_path)

    interval = 2  # 设置时间段间隔
    sorted_time_periods, max_bullet_count, high_light_time = summarize_bullet_count_by_interval(bullet_data, interval)

    bullet_count_chart = generate_bullet_count_chart(sorted_time_periods, high_light_time)

    highlight_info = generate_highlight_info(high_light_time, max_bullet_count)

    highlight_chart_path = 'highlight_distribution.html'
    bullet_count_chart.render(highlight_chart_path)

    with open(highlight_chart_path, 'a', encoding='utf-8') as f:
        f.write(f"<div style='font-size:20px; padding-left:100px;'>\n{highlight_info}\n</div>")

    file_url = os.path.abspath(highlight_chart_path)
    webbrowser.open(f'file://{file_url}')

if __name__ == "__main__":
    main()
