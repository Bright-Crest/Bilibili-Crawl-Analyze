import os
import json
import time
import random
import requests
import time
import pandas as pd
import xml.etree.ElementTree as ET
from typing import Dict, List

class BilibiliCrawler:
    def __init__(self):
        """初始化爬虫，设置必要的请求头和接口URL"""
        cookie = self._get_cookie_from_search()
        
        # B站支持的User-Agent列表
        self.user_agents = [
            # Chrome
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            # Firefox
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.3; rv:123.0) Gecko/20100101 Firefox/123.0',
            # Edge
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
        ]
        
        self.headers = {
            'User-Agent': random.choice(self.user_agents),
            'Referer': 'https://www.bilibili.com',
            'Cookie': cookie,
            'Origin': 'https://www.bilibili.com'
        }
        
        self.video_info_url = "https://api.bilibili.com/x/web-interface/view"
        self.comment_url = "https://api.bilibili.com/x/v2/reply/main"
        self.danmaku_url = "https://api.bilibili.com/x/v1/dm/list.so"

    def _make_request(self, url: str, params: Dict = None, retry_count: int = 3) -> requests.Response:
        """统一的请求处理方法"""
        for i in range(retry_count):
            try:
                # 每次请求都更新User-Agent
                self.headers['User-Agent'] = random.choice(self.user_agents)
                
                # 降低延迟时间
                time.sleep(random.uniform(0.2, 0.5))  # 200-500ms的随机延迟
                
                response = requests.get(
                    url,
                    params=params,
                    headers=self.headers,
                    timeout=5  # 减少超时时间
                )
                
                if response.status_code == 412:
                    print(f"请求被拦截，更换User-Agent后重试...")
                    time.sleep(random.uniform(1, 2))  # 被拦截时稍微多等一下
                    continue
                    
                if response.status_code == 200:
                    return response
                    
            except Exception as e:
                print(f"请求出错 (尝试 {i + 1}/{retry_count}): {str(e)}")
                if i < retry_count - 1:
                    time.sleep(random.uniform(0.5, 1))
                    continue
                    
        raise Exception("请求失败，已达到最大重试次数")

    def get_video_info(self, bv_id: str) -> Dict:
        """获取视频基本信息"""
        try:
            params = {'bvid': bv_id}
            response = self._make_request(self.video_info_url, params)
            data = response.json()
            
            if data['code'] == 0:
                info = data['data']
                return {
                    'title': info['title'],
                    'desc': info['desc'],
                    'pubdate': info['pubdate'],
                    'view': info['stat']['view'],
                    'like': info['stat']['like'],
                    'coin': info['stat']['coin'],
                    'favorite': info['stat']['favorite'],
                    'author': {
                        'name': info['owner']['name'],
                        'uid': info['owner']['mid']
                    },
                    'aid': info['aid']
                }
            else:
                raise Exception(f"获取视频信息失败: {data['message']}")
                
        except Exception as e:
            print(f"获取视频信息时发生错误: {str(e)}")
            return {}

    def get_danmaku(self, bv_id: str) -> List[Dict]:
        """获取视频弹幕"""
        try:
            # 先获取cid
            video_info = self.get_video_info(bv_id)
            if not video_info:
                raise Exception("获取视频信息失败")
            
            # 获取视频的cid
            params = {'bvid': bv_id}
            response = self._make_request(self.video_info_url, params)
            data = response.json()
            
            if data['code'] != 0:
                raise Exception(f"获取cid失败: {data['message']}")
            
            cid = data['data']['cid']
            
            # 获取弹幕XML
            danmaku_url = f"https://comment.bilibili.com/{cid}.xml"
            response = self._make_request(danmaku_url)
            response.encoding = 'utf-8'
            
            # 解析XML
            root = ET.fromstring(response.text)
            danmaku_list = []
            
            for d in root.findall('d'):
                try:
                    p = d.get('p', '').split(',')
                    if len(p) >= 8:
                        danmaku_list.append({
                            'time': float(p[0]),
                            'type': int(p[1]),
                            'color': int(p[3]),
                            'timestamp': int(p[4]),
                            'pool': int(p[5]),
                            'user_hash': p[6],
                            'dmid': p[7],
                            'text': d.text or ''
                        })
                except (ValueError, IndexError) as e:
                    print(f"解析弹幕数据出错: {str(e)}")
                    continue
                
            print(f"成功获取 {len(danmaku_list)} 条弹幕")
            return danmaku_list
            
        except Exception as e:
            print(f"获取弹幕时发生错误: {str(e)}")
            return []

    def _get_cookie_from_search(self) -> str:
        """从search.py文件中读取Cookie"""
        try:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # search.py在同一目录下
            search_path = os.path.join(current_dir, 'search.py')
            
            if not os.path.exists(search_path):
                print(f"找不到search.py文件: {search_path}")
                return ''
                
            with open(search_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 查找Cookie变量的定义
                cookie_start = content.find('Cookie = "') + len('Cookie = "')
                cookie_end = content.find('"', cookie_start)
                
                if cookie_start > 0 and cookie_end > cookie_start:
                    return content[cookie_start:cookie_end]
                else:
                    print("在search.py中找不到Cookie配置")
                    return ''
                    
        except Exception as e:
            print(f"无法从search.py读取Cookie: {str(e)}")
            print("请确保search.py中已配置正确的Cookie")
            return ''

    def get_comments(self, bv_id: str, page: int = 1) -> Dict:
        """获取视频评论"""
        try:
            aid = self._bv_to_aid(bv_id)
            if not aid:
                raise Exception("无法获取aid")
            
            params = {
                'type': 1,
                'oid': aid,
                'pn': page,
                'ps': 20,  # 每页20条评论
                'sort': 2,  # 按时间排序
                'nohot': 1  # 不包含热门评论
            }
            
            response = self._make_request(self.comment_url, params)
            data = response.json()
            
            if data['code'] == 0:
                # 新版API中评论总数在cursor.all_count中
                cursor = data['data'].get('cursor', {})
                total = cursor.get('all_count', 0)
                
                result = {
                    'comments': [],
                    'total': total
                }
                
                replies = data['data'].get('replies', [])
                if replies is None:  # API可能返回None而不是空列表
                    replies = []
                    
                for reply in replies:
                    comment = {
                        'text': reply['content']['message'],
                        'like': reply['like'],
                        'user': reply['member']['uname'],
                        'time': reply['ctime'],
                        'replies': []
                    }
                    # 获取评论的回复
                    if reply.get('replies'):
                        for sub_reply in reply['replies']:
                            comment['replies'].append({
                                'text': sub_reply['content']['message'],
                                'like': sub_reply['like'],
                                'user': sub_reply['member']['uname'],
                                'time': sub_reply['ctime']
                            })
                    result['comments'].append(comment)
                
                print(f"当前页评论数: {len(result['comments'])}")
                print(f"总评论数: {total}")
                
                return result
            else:
                raise Exception(f"获取评论失败: {data['message']}")
            
        except Exception as e:
            print(f"获取评论时发生错误: {str(e)}")
            return {'comments': [], 'total': 0}

    def _bv_to_aid(self, bv_id: str) -> int:
        """BV号转AV号（aid）的辅助方法
        
        Args:
            bv_id: 视频的BV号
            
        Returns:
            转换后的AV号
        """
        try:
            # 直接通过video_info接口获取aid
            params = {'bvid': bv_id}
            response = requests.get(
                self.video_info_url, 
                params=params, 
                headers=self.headers
            )
            data = response.json()
            if data['code'] == 0:
                return data['data']['aid']
            else:
                raise Exception(f"获取aid失败: {data['message']}")
        except Exception as e:
            print(f"BV号转AV号时发生错误: {str(e)}")
            return 0

    def _get_cid(self, bv_id: str) -> int:
        """获取视频的cid的辅助方法"""
        params = {'bvid': bv_id}
        response = requests.get(
            self.video_info_url, 
            params=params, 
            headers=self.headers
        )
        data = response.json()
        if data['code'] == 0:
            return data['data']['cid']
        return 0

    def save_to_file(self, data: Dict, filename: str):
        """将爬取的数据保存到文件
        
        Args:
            data: 要保存的数据
            filename: 文件名
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_comments(self, bv_id: str, filename: str = 'comments.json'):
        """保存评论到JSON，包含完整的评论信息"""
        try:
            comments_data = self.get_comments(bv_id)
            if not comments_data or not comments_data['comments']:
                print("未获取到评论数据")
                return
            
            # 构建更详细的评论数据结构
            result = {
                'total_count': comments_data['total'],
                'bvid': bv_id,
                'comments': []
            }
            
            for comment in comments_data['comments']:
                comment_info = {
                    'text': comment['text'],
                    'like': comment['like'],
                    'user': {
                        'name': comment['user'],
                        'time': comment['time'],
                    },
                    'replies': [{
                        'text': reply['text'],
                        'like': reply['like'],
                        'user': {
                            'name': reply['user'],
                            'time': reply['time']
                        },
                        'reply_to': comment['user']
                    } for reply in comment.get('replies', [])]
                }
                result['comments'].append(comment_info)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"评论数据已保存到 {filename}")
            
        except Exception as e:
            print(f"保存评论时发生错误: {str(e)}")

    def save_danmaku(self, bv_id: str, filename: str = 'danmaku.json'):
        """保存弹幕到JSON，包含完整的弹幕信息"""
        try:
            danmaku_list = self.get_danmaku(bv_id)
            if not danmaku_list:
                print("未获取到弹幕数据")
                return
            
            result = {
                'bvid': bv_id,
                'total_count': len(danmaku_list),
                'danmaku': [{
                    'time': dm['time'],
                    'type': dm['type'],
                    'color': dm['color'],
                    'timestamp': dm['timestamp'],
                    'pool': dm['pool'],
                    'user_hash': dm['user_hash'],
                    'dmid': dm['dmid'],
                    'text': dm['text'],
                    'font_size': 25,  # 默认字体大小
                    'mode': {
                        1: '滚动',
                        4: '底部',
                        5: '顶部'
                    }.get(dm['type'], '未知')
                } for dm in danmaku_list]
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"弹幕数据已保存到 {filename}")
            
        except Exception as e:
            print(f"保存弹幕时发生错误: {str(e)}")

    def crawl_all(self, bv_id: str):
        """爬取并保存所有数据
        
        Args:
            bv_id: 视频的BV号
        """
        # 获取并保存视频信息
        video_info = self.get_video_info(bv_id)
        self.save_to_file(video_info, 'video_info.json')
        
        # 获取并保存评论
        self.save_comments(bv_id)
        
        # 获取并保存弹幕
        self.save_danmaku(bv_id)

    def save_video_info(self, bv_id: str, filename: str = 'video_info.json'):
        """保存视频信息到JSON，保留所有可能的信息"""
        try:
            video_info = self.get_video_info(bv_id)
            if not video_info:
                print("未获取到视频信息")
                return
            
            # 保存完整的原始数据
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(video_info, f, ensure_ascii=False, indent=2)
            print(f"视频信息已保存到 {filename}")
            
        except Exception as e:
            print(f"保存视频信息时发生错误: {str(e)}")

# 仅用于测试和示例
if __name__ == "__main__":
    """
    这是一个简单的测试用例，实际使用请通过 main.py 运行
    用法示例：
    - 测试单个视频爬取
    - 开发时快速调试
    - 作为API使用参考
    """
    crawler = BilibiliCrawler()
    test_bv_id = "BV1cniBY6EJk"
    crawler.crawl_all(test_bv_id)
