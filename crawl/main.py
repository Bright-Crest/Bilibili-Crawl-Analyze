import json
import time
from typing import List
from crawler import BilibiliCrawler
from search import get_page
from concurrent.futures import ThreadPoolExecutor
import queue
import os

class BilibiliDataCollector:
    def __init__(self, keyword: str, max_pages: int = 10):
        self.keyword = keyword
        self.max_pages = max_pages
        self.crawler = BilibiliCrawler()
        self.pageQ = queue.Queue()
        
    def collect_bv_ids(self) -> List[str]:
        """收集视频BV号"""
        # 清空结果文件
        with open('result.txt', 'w', encoding='utf-8') as f:
            f.write("")
            
        # 初始化页码队列
        for i in range(1, self.max_pages + 1):
            self.pageQ.put(i)
        
        # 使用线程池搜索视频
        with ThreadPoolExecutor(max_workers=3) as executor:
            while not self.pageQ.empty():
                page = self.pageQ.get()
                executor.submit(get_page, page)
        
        # 读取结果文件中的BV号
        bv_ids = []
        with open('result.txt', 'r', encoding='utf-8') as f:
            bv_ids = [line.strip() for line in f if line.strip()]
            
        return bv_ids
    
    def collect_video_data(self, bv_ids: List[str], output_dir: str = 'data'):
        """并行收集视频数据"""
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        def process_video(bv_id: str):
            try:
                print(f"\n开始收集视频 {bv_id} 的数据...")
                
                # 创建视频专属目录
                video_dir = os.path.join(output_dir, bv_id)
                os.makedirs(video_dir, exist_ok=True)
                
                # 获取视频信息
                video_info = self.crawler.get_video_info(bv_id)
                if video_info:
                    with open(os.path.join(video_dir, 'video_info.json'), 'w', encoding='utf-8') as f:
                        json.dump(video_info, f, ensure_ascii=False, indent=2)
                
                # 获取评论
                self.crawler.save_comments(bv_id, os.path.join(video_dir, 'comments.json'))
                
                # 获取弹幕
                self.crawler.save_danmaku(bv_id, os.path.join(video_dir, 'danmaku.csv'))
                
            except Exception as e:
                print(f"处理视频 {bv_id} 时出错: {str(e)}")
        
        # 使用线程池并行处理视频
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(process_video, bv_ids)
    
    def run(self):
        """运行数据收集流程"""
        print(f"开始收集关键词 '{self.keyword}' 相关的视频数据...")
        
        # 1. 收集BV号
        bv_ids = self.collect_bv_ids()
        print(f"共找到 {len(bv_ids)} 个视频")
        
        # 2. 收集视频数据
        output_dir = f'data_{self.keyword}_{time.strftime("%Y%m%d_%H%M%S")}'
        self.collect_video_data(bv_ids, output_dir)
        
        print(f"\n数据收集完成！数据保存在 {output_dir} 目录下")

if __name__ == '__main__':
    # 使用示例
    keyword = "原神"  # 设置搜索关键词
    collector = BilibiliDataCollector(keyword, max_pages=5)  # 设置爬取前5页的视频
    collector.run() 