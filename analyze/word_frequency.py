import os
import jieba
from collections import Counter

from config import IS_DEBUG


# 停用词文件路径
stopwords_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cn_stopwords.txt')


def word_split(text_file, word_split_file, is_append=False):
    # 读取停用词
    with open(stopwords_path, 'r', encoding='utf-8') as f:
        stop_words = set([line.strip() for line in f])

    #------------------------------------中文分词------------------------------------
    mode = 'a' if is_append else 'w'
    with open(word_split_file, mode, encoding='utf-8') as f:
        for line in open(text_file, encoding='utf-8'):
            line = line.strip('\n')  # Ensure line.strip() affects line
            seg_list = jieba.cut(line, cut_all=False)
            # 过滤掉停用词
            seg_list_filtered = [word for word in seg_list if word not in stop_words]
            cut_words = " ".join(seg_list_filtered)
            f.write(cut_words + "\n")  # Ensure each line is written separately


def count(word_split_file, word_freq_file):
    # 为了词频统计，我们需要把所有分词结果合并在一起
    with open(word_split_file, 'r', encoding='utf-8') as f:
        all_words = f.read().split()

    # 词频统计
    c = Counter()
    for x in all_words:
        if len(x) > 1 and x != '\r\n':
            c[x] += 1

    if IS_DEBUG:
        # 输出词频最高的前10个词
        print('\n词频统计结果：')
        for (k, v) in c.most_common(10):
            print("%s:%d" % (k, v))
    
    # 存储数据
    with open(word_freq_file, 'w', encoding='utf-8') as fw:
        i = 1
        for (k, v) in c.most_common(len(c)):
            fw.write(str(i) + ',' + str(k) + ',' + str(v) + '\n')
            i = i + 1


def word_freq_count(text_file, word_freq_file):
    tmp_file = os.path.join(os.path.dirname(text_file), "." + os.path.basename(text_file).rsplit('.', 1)[0] + "_word_split.txt")
    word_split(text_file, tmp_file)
    count(tmp_file, word_freq_file)
    os.remove(tmp_file)
