
## B 站视频爬取分析

### 简述

该工具用于对已爬取出的`BiliBili`视频及其对应评论、弹幕数据进行分析统计，并生成相应的可视化图表，类型包括柱状图、散点图和折线图。

### 功能概述

- **视频分析**：分析视频播放量
- **评论分析**：分析每日评论数
- **弹幕分析**：分析弹幕情感倾向和分布时刻

### 安装依赖

请确保您的环境中已安装以下依赖库：

- Python 3.x
- `pyecharts`：用于生成图表
- `snownlp`：用于情感分析
- `csv`：用于读取弹幕数据文件
- `webbrowser`：用于自动打开生成的HTML文件
- `scipy`：用于衡量两个变量之间的线性关系强度与方向
- `matplotlib`: 画图
- `scikit-learn`: k-means聚类

安装：
```bash
pip install requests pandas jieba snownlp pyecharts scipy matplotlib scikit-learn
```

### 使用方法

#### 1. 准备爬取出的弹幕数据文件

将爬取的视频、评论、弹幕信息保存为 json 格式文件


#### 2. 运行分析工具

```bash
python bullet_emotion_analysis.py # 分析弹幕情感倾向，生成情感分析柱状图
python view_date_analysis.py # 分析播放量与发布日期之间的线性关系
python highlight_search.py # 从弹幕数量分析视频高光时刻
python video_active.py # 从评论数量分析视频日活量变化
python test.py # 进行词频、词云、kmeans分析
```

#### 3. 查看结果

运行脚本后，生成 `emotion_distribution.html` `highlight_distribution.html` `highlight_distribution.html` `daily_activity.html` 文件会根据 `bv` 号出现在爬取目录下每一个目录中。您将看到以下内容：

- **弹幕情感分布**：展示每种情感（非常负面、负面、中性、正面、非常正面）的弹幕数量和比例。
- **弹幕时间分布图**：展示每个时间段内的弹幕数量，且会将弹幕最多的时间段标记为高光时刻并显示具体信息。
- **播放量与发布日期散点图**：分析分析播放量与发布日期之间的线性关系强弱
- **时间段评论数量图**：展示该视频每日评论数量，从中分析视频日活量变化

