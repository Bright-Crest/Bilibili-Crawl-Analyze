import re
import os

import utils


#定义机械压缩去重函数
def compress(st):
    for i in range(1,int(len(st)/2)+1):
        for j in range(len(st)):
            if st[j:j+i] == st[j+i:j+2*i]:
                k = j + i
                while st[k:k+i] == st[k+i:k+2*i] and k<len(st): 
                    k = k + i
                st = st[:j] + st[k:]   
    return st


def clean_content(text_list):
    """
    清洗弹幕内容，去除每行前面的无效内容
    """
    cleaned_text_list = []

    for text in text_list:
        # 去除每行前面的无效内容，只保留中文字符、英文字符、数字和标点符号
        text = re.sub(r'^[^\u4e00-\u9fa5a-zA-Z0-9，。！？、；：‘’“”（）【】《》]*', '', text)
        text = compress(text)
        # 去除空白行
        if text.strip():
            cleaned_text_list.append(text.strip())

    return cleaned_text_list


def write_file(file_path, text_list, is_append):
    mode = 'a' if is_append else 'w'
    with open(file_path, mode, encoding='utf-8') as file:
        for text in text_list:
            file.write(text + '\n')


def clean(input_file_path, output_file_path, is_append=False):
    is_danmaku = ("danmaku" == os.path.basename(input_file_path).rsplit('.', 1)[0])
    text_list = []
    if is_danmaku:
        text_list = utils.read_danmu_file(input_file_path)
    else:
        text_list = utils.read_comments_file(input_file_path)
    # 清洗弹幕内容
    cleaned_text_list = clean_content(text_list)
    # 将清洗后的内容写入新文件
    write_file(output_file_path, cleaned_text_list, is_append)
