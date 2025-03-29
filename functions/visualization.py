import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from requests.exceptions import JSONDecodeError
from wordcloud import WordCloud
from collections import Counter
from sklearn.decomposition import PCA

class Visualization:

    @staticmethod
    def wordcloud(tracklist_clust):
        for cluster in tracklist_clust["cluster"].unique():
            text = " ".join(tracklist_clust[tracklist_clust["cluster"] == cluster]["track_tags"].dropna())
            
            wordcloud = WordCloud(width=400, height=200, background_color="white").generate(text)
            
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.axis("off")
            plt.title(f"Word cloud for different music styles in clusters {cluster}")
            plt.show()

    @staticmethod
    def counter(tracklist_clust):
        for cluster in tracklist_clust["cluster"].unique():
            all_artists = ",".join(tracklist_clust[tracklist_clust["cluster"] == cluster]["track_artists_id"].dropna()).split(", ")
            
            artist_counts = Counter(all_artists)
            most_common_artists = artist_counts.most_common(10)

            if len(most_common_artists) == 0:
                print(f"No artists found in cluster {cluster}")
                continue
            
            artists, counts = zip(*most_common_artists)
            
            plt.figure(figsize=(10, 5))
            sns.barplot(x=list(counts), y=list(artists), palette="viridis")
            plt.title(f"Top 10 artists - Cluster {cluster}")
            plt.xlabel("Occurrences")
            plt.ylabel("Artists")
            plt.show()

    @staticmethod
    def scatter_plot(X, Y=None):
        """
        X : one features from which we want to get a scatter plot ! it need to be a vector features ! 
        Y : one other features we want to observe the repartition for the plot (None by default)

        Return a scatter plot, using PCA method to divide data
        """
        X = X.apply(pd.Series).fillna(0)

        pca = PCA(n_components=2)

        X_pca = pca.fit_transform(X)

        plt.figure(figsize=(12, 6))

        sns.scatterplot(x=X_pca[:,0], y=X_pca[:,1], hue=Y, palette="viridis")
        plt.title(f"Scatter Plot {X.columns} PCA")

        plt.tight_layout()
        plt.show()

    @staticmethod
    def pairplot(df, Y=None):
        """
        df : features for a tracklist
        Y : features we want to observe repartition of the plot (None by default)
        Return a pairplot corresponding to the dataframe df
        """
        plt.figure(figsize=(12, 6))
        sns.pairplot(data=df, hue=Y, diag_kind='hist')
        plt.show()

    @staticmethod
    def histplot(X):
        """ 
        X : one specific features of a tracklist
        Return a histplot of this features
        """
        sns.histplot(X, kde=True)
        plt.title(f"{X.columns} histogram")
        plt.show()

    @staticmethod
    def correlation_heatmap(df):
        """
        df : features of a tracklist
        Return a correlation heatmap of the df's features
        """
        corr = df.corr()
        plt.figure(figsize=(10, 10))
        sns.heatmap(corr, annot=True, cmap='coolwarm')
        plt.title("Features Correlation Heatmap")
        plt.show()