import os
import json
from typing import List
from crawler import BilibiliCrawler
from concurrent.futures import ThreadPoolExecutor
import time

def read_bv_ids(filename: str = 'result.txt') -> List[str]:
    """从文件中读取BV号列表"""
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 返回上一级目录
    parent_dir = os.path.dirname(current_dir)
    # 构建result.txt的完整路径
    file_path = os.path.join(parent_dir, filename)
    
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在！")
        print("请按以下步骤操作：")
        print("1. 先运行 search.py 或 search_hot.py 生成视频列表")
        print("2. 确保 result.txt 文件已生成在正确位置")
        return []
        
    with open(file_path, 'r', encoding='utf-8') as f:
        bv_ids = [line.strip() for line in f if line.strip()]
        print(f"成功从 {filename} 读取到 {len(bv_ids)} 个BV号")
        return bv_ids

def create_output_dir(dirname: str = 'crawled_data'):
    """创建输出目录"""
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return dirname

def process_video(args):
    """处理单个视频的数据爬取"""
    crawler, bv_id, video_dir, index, total = args
    try:
        print(f"\n正在处理第 {index}/{total} 个视频 (BV号: {bv_id})")
        
        if not os.path.exists(video_dir):
            os.makedirs(video_dir)
        
        # 保存数据为JSON格式
        crawler.save_video_info(bv_id, os.path.join(video_dir, 'video_info.json'))
        crawler.save_comments(bv_id, os.path.join(video_dir, 'comments.json'))
        crawler.save_danmaku(bv_id, os.path.join(video_dir, 'danmaku.json'))
        
        print(f"视频 {bv_id} 的数据已保存到 {video_dir}")
        return True
        
    except Exception as e:
        print(f"处理视频 {bv_id} 时出错: {str(e)}")
        return False

def main():
    # 读取BV号列表
    bv_ids = read_bv_ids()
    if not bv_ids:
        return
    
    print(f"共读取到 {len(bv_ids)} 个视频的BV号")
    
    # 创建输出目录
    output_dir = create_output_dir()
    
    # 初始化爬虫
    crawler = BilibiliCrawler()
    
    # 准备任务参数
    tasks = [
        (crawler, bv_id, os.path.join(output_dir, bv_id), i+1, len(bv_ids))
        for i, bv_id in enumerate(bv_ids)
    ]
    
    # 使用线程池并行处理
    start_time = time.time()
    success_count = 0
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_video, tasks))
        success_count = sum(1 for r in results if r)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n爬取完成！")
    print(f"成功爬取: {success_count}/{len(bv_ids)} 个视频")
    print(f"总耗时: {duration:.2f} 秒")
    print(f"平均每个视频耗时: {duration/len(bv_ids):.2f} 秒")

if __name__ == '__main__':
    main() 