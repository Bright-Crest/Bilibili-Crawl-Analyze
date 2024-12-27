
# 分析弹幕情感

from snownlp import SnowNLP
import json

def read_danmu_file(file_path):
    # 读取弹幕内容文件text字段

    bullet_text = []
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for item in data['danmaku']:
            bullet_text.append(item['text']) 
    
    return bullet_text

def analyze_emotion(danmakus):
    # 分析弹幕的情感
    emotions = [SnowNLP(danmu).sentiments for danmu in danmakus]
    return emotions

def main():
    input_file_path = './danmaku.json'
    danmakus = read_danmu_file(input_file_path)

    # 进行情感分析
    emotions = analyze_emotion(danmakus)
    average_emotion = sum(emotions) / len(emotions)

    print(f"所有弹幕的平均情感分数是: {average_emotion:.2f}")

    # 保存结果到文件
    with open('emotion_analysis_results.txt', 'w', encoding='utf-8') as file:
        file.write(f"所有弹幕的平均情感分数是: {average_emotion:.2f}\n")
        file.write("\n弹幕情感分数如下:\n")
        for idx, emotion in enumerate(emotions):
            file.write(f"弹幕 {idx + 1}: {emotion:.2f}\n")

    print("情感分析结果已保存到 emotion_analysis_results.txt")

if __name__ == "__main__":
    main()