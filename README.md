# Bilibili-Crawl-Analyze
Crawl and analyze Bilibili data. Assignment of Information Content Security

## 任务

对b站视频进行分类，爬取一个分类下的视频信息，可以包括视频本身信息、弹幕、评论、一些统计数据，对数据整理并统一格式，然后分析数据，可以有关键词、图表、解释等。

- 输入：字符串（关键词，即视频的分类）

- 输出：分析结果

进阶功能模块：随机爬取数据，分析出近期热点事件/热搜

- 无输入
- 输出：字符串（关键词，即视频的分类）列表

将进阶功能的输出循环输入基础功能就可以自动分析热点事件。

### 信息爬取

#### API

输入：字符串（关键词，即视频的分类）

输出：

- 统计数据
  - 用json格式或excel等，具体细节待协商
- 评论和弹幕
  - 主要是字符串，具体待协商

#### 实现思路

主要利用bilibili-api，参考[1]。

一种思路是：

1. 先爬取搜索某个关键词出现的视频的链接或id，可参考[4]
2. 再爬取这些视频统计数据
   - 大部分都可以参考
3. 爬取视频评论
   - 参考[7]
4. 爬取视频弹幕
   - [7] 中提供的方法获取不完全，可以通过自动下载视频的方式自动下载弹幕，参考[3]

### 分析数据

#### API

输入：即信息爬取的输出

输出：分析结果，多多益善

#### 思路

先清洗数据

##### 统计数据

画表、画图

##### 评论和弹幕

参考[5]

- 关键词提取
- 高频词分析，如

参考[3]

- 词云
- 精彩片段、高能时刻

- 情感分析，如：

对于图表的详细解释参考[5]。

### 参考

1. [bilibili-api 开发文档](https://nemo2011.github.io/bilibili-api/#/)

2. [Ghauster/Bilivideoinfo: Bilibili视频数据爬虫 精确爬取完整的b站视频数据，包括标题、up主、up主id、精确播放数、历史累计弹幕数、点赞数、投硬币枚数、收藏人数、转发人数、发布时间、视频时长、视频简介、作者简介和标签](https://github.com/Ghauster/Bilivideoinfo)
   - 统计数据

3. [XavierJiezou/python-danmu-analysis](https://github.com/XavierJiezou/python-danmu-analysis?tab=readme-ov-file)
   - 弹幕
   - 有分析
4. [wanglishuai123/bili: 哔哩哔哩爬虫，每天定时爬取关键字的所有视频信息](https://github.com/wanglishuai123/bili)
   - 关键词搜索
5. [cyx031006/Crawler-Data-analysis: 哔哩哔哩_B站_Bilibili视频弹幕爬取与数据分析python ](https://github.com/cyx031006/Crawler-Data-analysis)
   - 弹幕
   - 有分析，且有详细解释
6. [Python：抓取 Bilibili（B站）评论、弹幕、字幕等_python爬取b站评论-CSDN博客](https://blog.csdn.net/qq_41297934/article/details/142284394)
   - 偏教程
7. [这才是B站爬虫的正确姿势，视频、评论、弹幕全部拿下 - 知乎](https://zhuanlan.zhihu.com/p/357392015)
   - 偏教程，提供了一些思路。推荐看看
