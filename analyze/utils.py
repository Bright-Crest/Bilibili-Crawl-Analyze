import json


def read_danmu_file(file_path):
    # 读取弹幕内容文件text字段
    bullet_text = []
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for item in data['danmaku']:
            bullet_text.append(item['text']) 
    
    return bullet_text


def read_comments_file(file_path):
    # 读取文件text字段
    text_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for item in data['comments']:
            text_list.append(item['text']) 
            for reply in item['replies']:
                text_list.append(reply['text'].split(':', 1)[-1])
    
    return text_list
