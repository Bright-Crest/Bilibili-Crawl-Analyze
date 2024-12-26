import json
import requests
import time
import threading
import queue
import random
from concurrent.futures import ThreadPoolExecutor

lock = threading.Lock()
pageQ = queue.Queue()
key = "原神" # 搜索关键词
# 在浏览器登录后f12查看cookie，填入下面的变量中
Cookie = "buvid3=41CC8967-7AEA-E636-7552-8B8F4E000FAD65451infoc; b_nut=1731505165; _uuid=96910C12E-12BA-FD49-B9CD-6C23184B8107C48655infoc; buvid_fp=5b920de7793a6f9e328ed9b9bc038619; buvid4=CB2F6860-22AC-A044-3CB4-90DC0DD8B1C566546-024111313-WdCW6kpkJsEgRp%2FNSmR0TA%3D%3D; rpdid=|(JJmY)YR|l|0J'u~Ju~J)u~|; DedeUserID=354559240; DedeUserID__ckMd5=02759c77df99598e; header_theme_version=CLOSE; enable_web_push=DISABLE; home_feed_column=5; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzU0Mzg3NjgsImlhdCI6MTczNTE3OTUwOCwicGx0IjotMX0.Qh8fUlXyjXECPN5Aw63iG_U0JipwScDWOzRgllDZsY0; bili_ticket_expires=1735438708; SESSDATA=e99a072b%2C1750731577%2C8f04a%2Ac1CjC74z1JdeB8i4vx0iJ_F1ILftW-nK_GZUnk5Vk3XqX-wqKTBir2lK7AdayDPz2R9HQSVmJJVXZ5UkQ5c3Rpa1hvcFJlWVJsVDlTQlE0VkNIWnplYk93T3gtdkw2akFNRkt4b1BnUk9OUm1zMURpYUZJVm9qdm05UjN3Z1hNZG43MzVXdlpNOEJBIIEC; bili_jct=255f2cb99fc2129aec36cbf77f24f7bb; b_lsid=A5C43DBD_194019D96B9; bsource=search_bing; is-2022-channel=1; browser_resolution=1659-834; sid=8t7gmhbx; bp_t_offset_354559240=1015148376909414400; CURRENT_FNVAL=2000"

def get_page(page, keyword=None, max_retries=3):
    if keyword is None:
        keyword = "原神"  # 默认关键词
    for retry in range(max_retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Referer': 'https://search.bilibili.com',
                'Cookie': Cookie
            }
            
            params = {
                'search_type': 'video',
                'keyword': keyword,
                'page': page,
                'page_size': 20,
            }
            
            api_url = "https://api.bilibili.com/x/web-interface/wbi/search/type"
            
            print(f"正在爬取第 {page} 页... (尝试 {retry + 1}/{max_retries})")
            time.sleep(random.uniform(0.5, 1))  # 增加延迟时间
            
            response = requests.get(api_url, params=params, headers=headers)
            json_data = response.json()
            
            # 验证响应数据结构
            if response.status_code != 200:
                print(f"页面 {page} 状态码错误: {response.status_code}")
                continue
                
            if 'data' not in json_data or 'result' not in json_data['data']:
                print(f"页面 {page} 数据结构异常: {json_data}")
                continue
                
            result = json_data['data']['result']
            if not result:
                print(f"页面 {page} 没有数据")
                return False
                
            bvid_list = []
            for video in result:
                if 'bvid' in video and video['bvid']:
                    bvid_list.append(video['bvid'])

            # 只有当bvid_list非空时才写入文件
            if bvid_list:  # 添加这个判断
                with lock:
                    with open('result.txt', 'a', encoding='utf-8') as f:
                        for bvid in bvid_list:
                            f.write(bvid + '\n')
                print(f"第 {page} 页bvid提取完成")
                return True
            else:
                print(f"第 {page} 页没有有效的bvid")
            
        except Exception as e:
            print(f"页面 {page} 出错 (尝试 {retry + 1}/{max_retries}): {str(e)}")
            if retry < max_retries - 1:
                time.sleep(random.uniform(5, 10))  # 出错后等待更长时间
                continue
            
    return False

if __name__ == '__main__':
    with open('result.txt', 'w', encoding='utf-8') as f:
        f.write("")
    # 放入页码
    for i in range(1, 11):
        pageQ.put(i)
    
    # 使用线程池处理任务
    with ThreadPoolExecutor(max_workers=3) as executor:
        while not pageQ.empty():
            page = pageQ.get()
            executor.submit(get_page, page)