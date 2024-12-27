# 用于获取当前热门视频，便于进行分析

import json
import requests
import time
import random
import threading
import queue
from concurrent.futures import ThreadPoolExecutor

lock = threading.Lock()
pageQ = queue.Queue()

def get_hot_video(page=1, max_retries=3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.bilibili.com/v/popular/all',
    }
    
    params = {
        'ps': 20,  # 每页数量
        'pn': page,  # 页码
    }
    
    api_url = "https://api.bilibili.com/x/web-interface/popular"
    
    for retry in range(max_retries):
        try:
            print(f"正在获取第{page}页热门视频列表... (尝试 {retry + 1}/{max_retries})")
            response = requests.get(api_url, headers=headers, params=params)
            
            if response.status_code != 200:
                print(f"状态码错误: {response.status_code}")
                continue
                
            json_data = response.json()
            if json_data['code'] != 0:
                print(f"API返回错误: {json_data['message']}")
                continue
                
            video_list = json_data['data']['list']
            
            with open('hot_videos.txt', 'a', encoding='utf-8') as f:
                for video in video_list:
                    bvid = video['bvid']
                    f.write(f"{bvid}\n")
                    
            print(f"成功获取第{page}页{len(video_list)}个热门视频")
            return True
            
        except Exception as e:
            print(f"发生错误 (尝试 {retry + 1}/{max_retries}): {str(e)}")
            if retry < max_retries - 1:
                time.sleep(random.uniform(2, 5))
                continue
    
    return False

if __name__ == '__main__':
    # 清空文件
    with open('result.txt', 'w', encoding='utf-8') as f:
        f.write('')
    
    # 添加页码到队列
    for i in range(1, 11):
        pageQ.put(i)
    
    # 使用线程池处理请求
    with ThreadPoolExecutor(max_workers=5) as executor:
        while not pageQ.empty():
            page = pageQ.get()
            executor.submit(get_hot_video, page)