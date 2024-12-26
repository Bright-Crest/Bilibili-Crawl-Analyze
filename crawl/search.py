import asyncio

from bilibili_api import video, search, sync

if __name__ == '__main__':
    for page in range(1, 10):
        result = sync(search.search_by_type("战地", search_type=search.SearchObjectType.VIDEO, page=page))
        with open('result.txt', 'a', encoding='utf-8') as f:
            for video in result['result']:
                f.write(video['bvid'] + '\n')
