import os

import clean
import word_frequency
import word_cloud
import kmeans


import highlight_search
import bullet_emotion_analysis
import view_date_analysis
import video_active


def get_word_freq(input_file, word_freq_file):
    cleaned_file = os.path.join(os.path.dirname(input_file), ".cleaned_" + os.path.basename(input_file).rsplit('.', 1)[0] + ".txt")
    clean.clean(input_file, cleaned_file)
    word_frequency.word_freq_count(cleaned_file, word_freq_file)
    os.remove(cleaned_file)


def get_overall_word_freq(input_file_list, word_freq_file):
    cleaned_file = os.path.join(os.path.dirname(word_freq_file), ".cleaned_text.txt")
    for file in input_file_list:
        clean.clean(file, cleaned_file, is_append=True)
    word_frequency.word_freq_count(cleaned_file, word_freq_file)
    os.remove(cleaned_file)


def get_kmeans_result(input_file_list, output_file):
    cleaned_file = os.path.join(os.path.dirname(output_file), ".cleaned_text.txt")
    for file in input_file_list:
        clean.clean(file, cleaned_file, is_append=True)
    word_split_file = os.path.join(os.path.dirname(output_file), ".split_text.txt")
    word_frequency.word_split(cleaned_file, word_split_file)
    kmeans.apply_kmeans(word_split_file, output_file, 5)
    os.remove(cleaned_file)
    os.remove(word_split_file)


def get_highlight_search():
    highlight_search.main()

def get_bullet_emotion_analysis():
    bullet_emotion_analysis.main()

def get_view_date_analysis():
    view_date_analysis.main()

def get_video_active():
    video_active.main()

def test():
    crawled_data_dir = './crawled_data'
    overall_analysis_output_dir = './overall_analysis_output'
    if not os.path.isdir(overall_analysis_output_dir):
        os.mkdir(overall_analysis_output_dir)
    
    # # 遍历所有 BV 号子目录
    # for bv_number in os.listdir(crawled_data_dir):
    #     bv_path = os.path.join(crawled_data_dir, bv_number)
    #     if os.path.isdir(bv_path):
    #         video_info = os.path.join(bv_path, "video_info.json")
    #         danmaku = os.path.join(bv_path, "danmaku.json")
    #         comments = os.path.join(bv_path, "comments.json")
    #         if os.path.isfile(danmaku):
    #             # danmaku word freq
    #             danmaku_wf = os.path.join(bv_path, "analyze", "danmaku_word_freq.csv")
    #             get_word_freq(danmaku, danmaku_wf)
    #             # danmaku word cloud
    #             danmaku_wc = os.path.join(bv_path, "analyze", "danmaku_word_cloud.html")
    #             word_cloud.create_word_cloud(danmaku_wf, danmaku_wc)
    #         if os.path.isfile(comments):
    #             # comments word freq
    #             comments_wf = os.path.join(bv_path, "analyze", "comments_word_freq.csv")
    #             get_word_freq(comments, comments_wf)
    #             # comments word cloud
    #             comments_wc = os.path.join(bv_path, "analyze", "comments_word_cloud.html")
    #             word_cloud.create_word_cloud(comments_wf, comments_wc)
    
    danmaku_file_list = []
    comments_file_list = []
    for bv_number in os.listdir(crawled_data_dir):
        bv_path = os.path.join(crawled_data_dir, bv_number)
        if os.path.isdir(bv_path):
            video_info = os.path.join(bv_path, "video_info.json")
            danmaku = os.path.join(bv_path, "danmaku.json")
            comments = os.path.join(bv_path, "comments.json")
            if os.path.isfile(danmaku):
                danmaku_file_list.append(danmaku)
            if os.path.isfile(comments):
                comments_file_list.append(comments)

    # danmaku word freq
    danmaku_wf = os.path.join(overall_analysis_output_dir, "danmaku_word_freq.csv")
    get_overall_word_freq(danmaku_file_list, danmaku_wf)
    # danmaku word cloud
    danmaku_wc = os.path.join(overall_analysis_output_dir, "danmaku_word_cloud.html")
    word_cloud.create_word_cloud(danmaku_wf, danmaku_wc)
    # comments word freq
    comments_wf = os.path.join(overall_analysis_output_dir, "comments_word_freq.csv")
    get_overall_word_freq(comments_file_list, comments_wf)
    # comments word cloud
    comments_wc = os.path.join(overall_analysis_output_dir, "comments_word_cloud.html")
    word_cloud.create_word_cloud(comments_wf, comments_wc)
    # all word freq
    all_wf = os.path.join(overall_analysis_output_dir, "all_word_freq.csv")
    get_overall_word_freq(danmaku_file_list + comments_file_list, all_wf)
    # all word cloud
    all_wc = os.path.join(overall_analysis_output_dir, "all_word_cloud.html")
    word_cloud.create_word_cloud(all_wf, all_wc)

    print('')
    all_kmeans = os.path.join(overall_analysis_output_dir, "all_kmeans.txt")
    get_kmeans_result(danmaku_file_list + comments_file_list, all_kmeans)

    get_highlight_search()
    get_bullet_emotion_analysis()
    get_view_date_analysis()
    get_video_active()

if __name__ == "__main__":
    test()
