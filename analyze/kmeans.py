import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA


def apply_kmeans(text_file, output_file, n=3):
    text_list = []
    with open(text_file, 'r', encoding='utf-8') as f:
        text_list = f.readlines()
        
    vectorizer = TfidfVectorizer(max_features=1000)
    X = vectorizer.fit_transform(text_list)

    num_clusters = min(n, len(text_list))
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(X)

    cluster = kmeans.labels_

    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names_out()

    for i in range(num_clusters):
        print(f"聚类 {i}:")
        for ind in order_centroids[i, :10]:
            print(f"\t{terms[ind]}")

    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X.toarray())

    plt.figure(figsize=(10, 8))
    colors = ['red', 'blue', 'green', 'purple', 'orange']
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
