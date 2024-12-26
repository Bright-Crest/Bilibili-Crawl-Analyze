import requests
import time
import json
from typing import Dict, List, Optional
import pandas as pd
import xml.etree.ElementTree as ET
import re

class BilibiliCrawler:
    def __init__(self):
        """初始化爬虫，设置必要的请求头和接口URL"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com',
            'Cookie': 'CURRENT_FNVAL=4048; b_lsid=10B4109FC_18C435D9C95; buvid_fp=45b2193579703f41227e409a2d07e448',
            'Origin': 'https://www.bilibili.com'
        }
        self.video_info_url = "https://api.bilibili.com/x/web-interface/view"
        self.comment_url = "https://api.bilibili.com/x/v2/reply/main"
        self.danmaku_url = "https://api.bilibili.com/x/v1/dm/list.so"

    def get_video_info(self, bv_id: str) -> Dict:
        """获取视频基本信息
        
        Args:
            bv_id: 视频的BV号
            
        Returns:
            包含视频信息的字典
        """
        try:
            params = {'bvid': bv_id}
            response = requests.get(
                self.video_info_url, 
                params=params, 
                headers=self.headers
            )
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
                    }
                }
            else:
                raise Exception(f"获取视频信息失败: {data['message']}")
                
        except Exception as e:
            print(f"获取视频信息时发生错误: {str(e)}")
            return {}

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
            
            response = requests.get(
                self.comment_url, 
                params=params, 
                headers=self.headers
            )
            
            # 打印请求URL和响应，用于调试
            print(f"请求URL: {response.url}")
            print(f"响应状态码: {response.status_code}")
            
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
                
                # 打印调试信息
                print(f"当前页评论数: {len(result['comments'])}")
                print(f"总评论数: {total}")
                
                return result
            else:
                raise Exception(f"获取评论失败: {data['message']}")
            
        except Exception as e:
            print(f"获取评论时发生错误: {str(e)}")
            return {'comments': [], 'total': 0}

    def get_danmaku(self, bv_id: str) -> List[str]:
        """获取视频弹幕
        
        Args:
            bv_id: 视频的BV号
            
        Returns:
            弹幕列表
        """
        try:
            cid = self._get_cid(bv_id)
            response = requests.get(
                f"https://comment.bilibili.com/{cid}.xml", 
                headers=self.headers
            )
            response.encoding = 'utf-8'
            # 这里需要解析XML格式的弹幕数据
            # 简单返回原始数据，实际使用时需要进行解析
            return response.text
            
        except Exception as e:
            print(f"获取弹幕时发生错误: {str(e)}")
            return []

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
        """保存视频评论到JSON文件"""
        all_comments = []
        page = 1
        total = None
        retry_count = 0
        max_retries = 3
        
        while True:
            try:
                result = self.get_comments(bv_id, page)
                comments = result['comments']
                
                if total is None:
                    total = result['total']
                    print(f"该视频共有{total}条评论")
                
                if not comments:
                    break  # 如果没有评论了就退出
                
                all_comments.extend(comments)
                print(f"已获取第{page}页评论，当前共{len(all_comments)}/{total}条")
                
                if len(all_comments) >= total or len(all_comments) >= 1000:  # 限制最多获取1000条评论
                    break
                    
                page += 1
                time.sleep(1)  # 减少等待时间
                
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    print(f"连续{max_retries}次出错，停止获取")
                    break
                print(f"获取第{page}页评论时出错: {str(e)}")
                time.sleep(2)
        
        if all_comments:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_comments, f, ensure_ascii=False, indent=2)
            print(f"已保存{len(all_comments)}条评论到{filename}")
        else:
            print("未获取到任何评论，跳过保存")

    def save_danmaku(self, bv_id: str, filename: str = 'danmus.csv'):
        """保存视频弹幕到CSV文件
        
        Args:
            bv_id: 视频的BV号
            filename: 保存的文件名
        """
        try:
            xml_content = self.get_danmaku(bv_id)
            root = ET.fromstring(xml_content)
            
            danmus = []
            for d in root.findall('d'):
                p_attrs = d.get('p').split(',')
                danmu = {
                    'time': float(p_attrs[0]),  # 弹幕出现时间
                    'type': int(p_attrs[1]),    # 弹幕类型
                    'color': int(p_attrs[3]),   # 弹幕颜色
                    'text': d.text              # 弹幕内容
                }
                danmus.append(danmu)
            
            # 转换为DataFrame并保存为CSV
            df = pd.DataFrame(danmus)
            df.sort_values('time', inplace=True)  # 按时间排序
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"已保存{len(danmus)}条弹幕到{filename}")
            
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

# 使用示例
if __name__ == "__main__":
    crawler = BilibiliCrawler()
    bv_id = "BV1cniBY6EJk"
    crawler.crawl_all(bv_id)
