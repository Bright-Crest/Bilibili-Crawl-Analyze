# B站视频数据爬虫

## 使用说明

#### 1.1 安装必要软件包
```bash
pip3 install requests
```

#### 1.2 获取B站Cookie
1. 在浏览器登录后f12查看Cookie
2. 将Cookie粘贴到search.py中的相应位置

### 2. 获取视频BV号列表

有两种方式可以获取视频列表：

#### 方式一：根据关键词搜索
```bash
python search.py
```
- 运行前请确保已在search.py中设置了正确的Cookie
- 默认搜索关键词为"原神"，可以在代码中修改
- 结果会保存到result.txt文件中，一行一个bv号

#### 方式二：获取热门视频
```bash
python search_hot.py
```
- 会自动爬取B站热门视频列表
- 结果同样保存到result.txt文件中

### 3. 爬取视频数据
```bash
python main.py
```
- 运行前请确保已在search.py中设置了正确的Cookie
- 程序会读取result.txt中的BV号
- 为每个视频创建独立的数据目录
- 并行爬取多个视频的数据

### 数据存储结构

爬取的数据将保存在`crawled_data`目录下，每个视频都有独立的子目录：

```
crawled_data/
    └── BV号/
        ├── video_info.json  (视频基本信息)
        ├── comments.json    (评论数据)
        └── danmaku.json    (弹幕数据)
```

### 数据格式说明

所有数据以JSON格式保存，包含完整的信息：

#### video_info.json
```json
{
    "title": "视频标题",
    "desc": "视频描述",
    "pubdate": "发布时间戳",
    "view": "播放量",
    "like": "点赞数",
    "coin": "投币数",
    "favorite": "收藏数",
    "author": {
        "name": "UP主名称",
        "uid": "UP主ID"
    },
    "aid": "视频AV号"
}
```

#### comments.json
```json
{
    "total_count": "评论总数",
    "bvid": "视频BV号",
    "comments": [
        {
            "text": "评论内容",
            "like": "点赞数",
            "user": {
                "name": "用户名",
                "time": "评论时间"
            },
            "replies": [
                {
                    "text": "回复内容",
                    "like": "点赞数",
                    "user": {
                        "name": "回复用户名",
                        "time": "回复时间"
                    },
                    "reply_to": "被回复用户名"
                }
            ]
        }
    ]
}
```

#### danmaku.json
```json
{
    "bvid": "视频BV号",
    "total_count": "弹幕总数",
    "danmaku": [
        {
            "time": "出现时间(秒)",
            "type": "弹幕类型",
            "color": "颜色(十进制)",
            "timestamp": "发送时间戳",
            "pool": "弹幕池",
            "user_hash": "用户哈希",
            "dmid": "弹幕ID",
            "text": "弹幕内容",
            "font_size": "字体大小",
            "mode": "显示模式(滚动/顶部/底部)"
        }
    ]
}
```

## 项目结构
```
crawl/
├── main.py          # 主程序入口，用于批量爬取视频
├── crawler.py       # 核心爬虫类，包含所有爬取功能
├── search.py        # 关键词视频搜索
├── search_hot.py    # 热门视频获取
└── readme.md        # 项目说明文档
```

### 文件说明
- **main.py**: 实际运行的主程序，用于批量处理视频爬取
- **crawler.py**: 核心功能模块，包含爬虫类和所有爬取方法
- **search.py**: 通过关键词搜索获取视频列表
- **search_hot.py**: 获取B站热门视频列表

### 运行顺序
1. 先运行 search.py 或 search_hot.py 获取视频列表
2. 然后运行 main.py 进行批量爬取
3. 注意：不要直接运行 crawler.py，它只是功能模块

