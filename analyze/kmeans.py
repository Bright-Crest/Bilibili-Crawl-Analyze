import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.metrics import silhouette_samples
# from adjustText import adjust_text

RANDOM_STATE = 0


def get_best_num_clusters(X):
    #先用轮廓系数绘制学习曲线找出最优类别数
    best_score = 0
    best_num_clusters = 2
    for k in range(2, 7):
        model = KMeans(n_clusters=k, random_state=RANDOM_STATE) 
        model = model.fit(X)
        score = silhouette_score(X,model.labels_)
        if score > best_score:
            best_score = score
            best_num_clusters = k
    return best_num_clusters


# def apply_PCA(X, kmeans: KMeans, text_list):
#     #用PCA降维数据后的分类结果
#     fig, ax = plt.subplots(figsize=(15, 15))
#     # 将聚类的结果和中心点的结果都画在原图里面
#     plt.scatter(X[:, 0], X[:, 1], c=kmeans.labels_, alpha=0.5)
#     plt.scatter(kmeans.cluster_centers_[: , 0], kmeans.cluster_centers_[:, 1], color = "red") #加上每一个的中心

#     new_texts = [plt.text(x, y, text, fontsize=12) for x, y, text in zip(X[:, 0], X[:, 1], text_list)]
#     adjust_text(new_texts, 
#                 only_move={'text': 'x'},
#                 arrowprops=dict(arrowstyle='-', color='grey'))

#     # 美观起见隐藏顶部与右侧边框线
#     ax.spines['right'].set_visible(False)
#     ax.spines['top'].set_visible(False)


def apply_kmeans(text_file, output_file):
    text_list = []
    with open(text_file, 'r', encoding='utf-8') as f:
        text_list = f.readlines()
        
    vectorizer = TfidfVectorizer(max_features=1000)
    X = vectorizer.fit_transform(text_list)

    num_clusters = get_best_num_clusters(X)
    kmeans = KMeans(n_clusters=num_clusters, random_state=RANDOM_STATE)
    kmeans.fit(X)

    cluster = kmeans.labels_

    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names_out()

    for i in range(num_clusters):
        print(f"聚类 {i}:")
        for ind in order_centroids[i, :10]:
            print(f"\t{terms[ind]}")

    with open(output_file.rsplit('.', 1)[0] + '.txt', 'w', encoding='utf-8') as fw:
        for i in range(num_clusters):
            fw.write(f"聚类 {i}:\n")
            for ind in order_centroids[i, :10]:
                fw.write(f"\t{terms[ind]}\n")
    
    with open(output_file.rsplit('.', 1)[0] + '_verbose.txt', 'w', encoding='utf-8') as fw:
        for i in range(num_clusters):
            fw.write(f"聚类 {i}:\n")
            for idx, c in enumerate(cluster):
                if c == i:
                    fw.write(f"\t{text_list[idx]}")

    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X.toarray())

    plt.figure(figsize=(10, 8))
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'yellow', 'brown']
    for i in range(num_clusters):
        points = X_pca[cluster==i]
        plt.scatter(points[:, 0], points[:, 1], s=50, c=colors[i], label=f"cluster {i}")
    
    plt.title(f'K-Means')
    plt.xlabel('PCA 1')
    plt.ylabel('PCA 2')
    plt.legend()
    plt.savefig(output_file.rsplit('.', 1)[0] + '.png')
    plt.waitforbuttonpress()
    plt.close()
    