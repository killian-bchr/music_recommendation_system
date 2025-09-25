import requests
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from requests.exceptions import JSONDecodeError
from kneed import KneeLocator
from scipy import stats
from datetime import datetime
from collections import Counter
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split


class Tracklist:

    def __init__(self, df):
        self.df = df

    def view_tracklist(self):
        return self.df

    def vectorize_recent_tracks(self, n_components=1, played_at=False):
        """
        df : dataframe with last tracks (returned by get_recent_track)
        n_components : number of components used in the PCA method (integer)
        played_at : to get this feature in the resulting dataframe (Boolean)

        Return a dataframe with vectorized data
        """
        # Define the encoder
        encoder = LabelEncoder()
        df = self.df.copy()
        df_vect = df[['popularity', 'duration', 'track_listeners', 'track_playcount', 'release_date']].copy()

        # Encode all the ids (so we don't need anymore name and titles)
        df_vect['album_id'] = encoder.fit_transform(df['album_id'])
        df_vect['track_id'] = encoder.fit_transform(df['track_id'])

        df['track_artists_id'] = df['track_artists_id'].fillna('').apply(lambda x: x.split(', '))
        df['album_artists_id'] = df['album_artists_id'].fillna('').apply(lambda x: x.split(', '))

        mlb = MultiLabelBinarizer()
        encoded_artists = pd.DataFrame(mlb.fit_transform(df['track_artists_id']))
        encoded_albums = pd.DataFrame(mlb.fit_transform(df['album_artists_id']))

        # Vectorize release_date : compare lifetime since reference date
        reference_date = datetime.strptime('01-01-2000', '%d-%m-%Y')
        df_vect['release_date'] = pd.to_datetime(df_vect['release_date'], errors='coerce')
        df_vect['release_date'] = (df_vect['release_date'] - reference_date).dt.days

        if played_at:
            # Vectorize played date : conserve cyclic relation with cos and sin

            df_vect['year'] = df['played_at'].dt.year
            df_vect['month'] = df['played_at'].dt.month
            df_vect['day'] = df['played_at'].dt.day
            df_vect['dayofweek'] = df['played_at'].dt.dayofweek  # 0 = Monday, 6 = Sunday
            df_vect['hour'] = df['played_at'].dt.hour

            df_vect['month_sin'] = np.sin(2 * np.pi * df_vect['month'] / 12)
            df_vect['month_cos'] = np.cos(2 * np.pi * df_vect['month'] / 12)
            df_vect['dayofweek_sin'] = np.sin(2 * np.pi * df_vect['dayofweek'] / 7)
            df_vect['dayofweek_cos'] = np.cos(2 * np.pi * df_vect['dayofweek'] / 7)
            df_vect['day_sin'] = np.sin(2 * np.pi * df_vect['day'] / 31)
            df_vect['day_cos'] = np.cos(2 * np.pi * df_vect['day'] / 31)


        # Vectorize similar_artists and track_tags
        unique_artists = df['similar_artists'].str.split(', ').explode().dropna()
        unique_artists = unique_artists[unique_artists != ''].unique().tolist()

        unique_tags = df['track_tags'].str.split(', ').explode().dropna()
        unique_tags = unique_tags[unique_tags != ''].unique().tolist()

        def vectorize_column(column, unique_values):
            return column.fillna('').str.split(', ').apply(lambda x: pd.Series(unique_values).isin(x).astype(int).tolist())
        
        similar_artists_vect = vectorize_column(df['similar_artists'], unique_artists)
        track_tags_vect = vectorize_column(df['track_tags'], unique_tags)

        ### Transform vector in float number
        pca = PCA(n_components=n_components)

        similar_artists_pca = pd.DataFrame(pca.fit_transform(similar_artists_vect.apply(pd.Series).fillna(0)), index=df.index)
        track_tags_pca = pd.DataFrame(pca.fit_transform(track_tags_vect.apply(pd.Series).fillna(0)), index=df.index)

        track_artists_pca = pd.DataFrame(pca.fit_transform(encoded_artists.fillna(0)), index=df.index)
        album_artists_pca = pd.DataFrame(pca.fit_transform(encoded_albums.fillna(0)), index=df.index)

        if n_components == 1:
            df_vect['similar_artists'] = similar_artists_pca.iloc[:, 0]
            df_vect['track_tags'] = track_tags_pca.iloc[:, 0]
            df_vect['track_artists_id'] = track_artists_pca.iloc[:, 0]
            df_vect['album_artists_id'] = album_artists_pca.iloc[:, 0]
        else:
            similar_artists_pca.columns = [f'similar_artists_{i}' for i in range(1, n_components + 1)]
            track_tags_pca.columns = [f'track_tags_{i}' for i in range(1, n_components + 1)]
            track_artists_pca.columns = [f'track_artists_id_{i}' for i in range(1, n_components + 1)]
            album_artists_pca.columns = [f'album_artists_id_{i}' for i in range(1, n_components + 1)]

            df_vect = pd.concat([df_vect, similar_artists_pca, track_tags_pca, track_artists_pca, album_artists_pca], axis=1)

        return df_vect

    def scale_and_weight(self, weights=None, n_components=1, played_at = False):
        """
        df : dataframe with last tracks (returned by get_recent_track)
        weights : a dictionnaire with features to be weights in key (string) and the wieght in value (float)
                            (ex : {'duration': 0.5, 'album_id': 500, 'album_artists_id': 1000, 'track_tags': 20})
                            after being scaled the default weight is 1
        n_components : number of components used in the PCA method (integer)
                    needs to be the same as usd in the precedent function (vectorization step) !

        Return a dataframe with weighted and scaled data
        """
        df_vect = self.vectorize_recent_tracks(n_components = n_components, played_at = played_at)
        scaler = StandardScaler()
        df_vect_scaled = pd.DataFrame(scaler.fit_transform(df_vect), columns=df_vect.columns, index=df_vect.index)

        if weights:
            for prefix, weight in weights.items():
                if prefix in df_vect_scaled.columns:
                    df_vect_scaled[prefix] *= weight
                else:
                    for i in range(1, n_components + 1):
                        col_name = f"{prefix}_{i}" if n_components > 1 else prefix
                        if col_name in df_vect_scaled.columns:
                            df_vect_scaled[col_name] *= weight
            
            #df_vect_scaled = pd.DataFrame(scaler.fit_transform(df_vect_scaled), columns=df_vect_scaled.columns, index=df_vect_scaled.index)

        return df_vect_scaled


class Cluster:

    def __init__(self, clusters, weights = None, n_components = 1):
        self.clusters = clusters
        self.weights = weights
        self.n_components = n_components

    def vectorize_tracklist(self):
        cluster_vect_dfs = {}

        for cluster_name, cluster in self.clusters.items():
            encoder = LabelEncoder()
            cluster = cluster.copy()
            cluster_vect = cluster[['popularity', 'duration', 'track_listeners', 'track_playcount']].copy()

            ### Encode all the ids
            cluster_vect['album_id'] = encoder.fit_transform(cluster['album_id'])
            cluster_vect['track_id'] = encoder.fit_transform(cluster['track_id'])

            cluster['track_artists_id'] = cluster['track_artists_id'].fillna('').astype(str).apply(lambda x: x.split(', '))
            cluster['album_artists_id'] = cluster['album_artists_id'].fillna('').astype(str).apply(lambda x: x.split(', '))

            mlb = MultiLabelBinarizer()
            encoded_artists = pd.DataFrame(mlb.fit_transform(cluster['track_artists_id']))
            encoded_albums = pd.DataFrame(mlb.fit_transform(cluster['album_artists_id']))

            reference_date = datetime.strptime('01-01-2000', '%d-%m-%Y')
            cluster_vect['release_date'] = (cluster['release_date'] - reference_date).dt.days

            # Vectorize similar_artists and track_tags
            unique_artists = cluster['similar_artists'].str.split(', ').explode().dropna()
            unique_artists = unique_artists[unique_artists != ''].unique().tolist()

            unique_tags = cluster['track_tags'].str.split(', ').explode().dropna()
            unique_tags = unique_tags[unique_tags != ''].unique().tolist()

            def vectorize_column(column, unique_values):
                return column.fillna('').str.split(', ').apply(lambda x: pd.Series(unique_values).isin(x).astype(int).tolist())
                
            similar_artists_vect = vectorize_column(cluster['similar_artists'], unique_artists)
            track_tags_vect = vectorize_column(cluster['track_tags'], unique_tags)

            ### On convertit les vecteurs en float
            pca = PCA(n_components=self.n_components)

            similar_artists_pca = pd.DataFrame(pca.fit_transform(similar_artists_vect.apply(pd.Series).fillna(0)), index=cluster_vect.index)
            track_tags_pca = pd.DataFrame(pca.fit_transform(track_tags_vect.apply(pd.Series).fillna(0)), index=cluster_vect.index)
            track_artists_pca = pd.DataFrame(pca.fit_transform(encoded_artists.fillna(0)), index=cluster_vect.index)
            album_artists_pca = pd.DataFrame(pca.fit_transform(encoded_albums.fillna(0)), index=cluster_vect.index)

            if self.n_components == 1:
                cluster_vect['similar_artists'] = similar_artists_pca.iloc[:, 0]
                cluster_vect['track_tags'] = track_tags_pca.iloc[:, 0]
                cluster_vect['track_artists_id'] = track_artists_pca.iloc[:, 0]
                cluster_vect['album_artists_id'] = album_artists_pca.iloc[:, 0]
            else:
                similar_artists_pca.columns = [f'similar_artists_{i}' for i in range(1, self.n_components + 1)]
                track_tags_pca.columns = [f'track_tags_{i}' for i in range(1, self.n_components + 1)]
                track_artists_pca.columns = [f'track_artists_id_{i}' for i in range(1, self.n_components + 1)]
                album_artists_pca.columns = [f'album_artists_id_{i}' for i in range(1, self.n_components + 1)]
                
                cluster_vect = pd.concat([cluster_vect, similar_artists_pca, track_tags_pca, track_artists_pca, album_artists_pca], axis=1)

            scaler = MinMaxScaler()
            cluster_vect_scaled = pd.DataFrame(scaler.fit_transform(cluster_vect), columns=cluster_vect.columns, index=cluster_vect.index)

            if self.weights:
                for prefix, weight in self.weights.items():
                    if prefix in cluster_vect_scaled.columns:
                        cluster_vect_scaled[prefix] *= weight
                    else:
                        for i in range(1, self.n_components + 1):
                            col_name = f"{prefix}_{i}" if self.n_components > 1 else prefix
                            if col_name in cluster_vect_scaled.columns:
                                cluster_vect_scaled[col_name] *= weight

            cluster_vect_dfs[cluster_name] = cluster_vect_scaled if not cluster_vect_scaled.empty else pd.DataFrame()

        return cluster_vect_dfs


    def compute_cosine_matrices(self):
        clusters_vect = self.vectorize_tracklist
        cosine_matrices = {}

        for num_cluster, cluster in clusters_vect.items():
            cluster = cluster.copy()
            cluster.drop(columns=['track_id'], inplace=True, errors='ignore')
            cosine_matrices[num_cluster] = cosine_similarity(cluster.fillna(0))

        return cosine_matrices
