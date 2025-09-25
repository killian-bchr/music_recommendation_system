from datetime import datetime

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


class DataPreprocessor:

    REFERENCE_DATE = datetime.strptime('01-01-2000', '%d-%m-%Y')

    def __init__(self, df):
        self.df = df.copy()

    def encode_ids(self, columns):
        encoder = LabelEncoder()
        for col in columns:
            self.df[col] = encoder.fit_transform(self.df[col])
        return self

    def binarize_multilabel_column(self, columns):
        mlb = MultiLabelBinarizer()
        all_encoded = []

        for col in columns:
            self.df[col] = self.df[col].apply(
                lambda x: x.split(', ') if isinstance(x, str) else []
            )

            encoded = pd.DataFrame(
                mlb.fit_transform(self.df[col]),
                index=self.df.index,
                columns=[f"{col}_{cls}" for cls in mlb.classes_]
            )
            all_encoded.append(encoded)

        encoded_df = pd.concat(all_encoded, axis=1)
        self.df.drop(columns=columns, inplace=True)
        self.df = pd.concat([self.df, encoded_df], axis=1)

        return self

    def vectorize_date(self, columns):
        for col in columns:
            self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
            self.df[col] = (self.df[col] - self.REFERENCE_DATE).dt.days
        return self

    def add_played_at_features(self):
        """Conserve cyclic relation with cos and sin"""
        self.df['year'] = self.df['played_at'].dt.year
        self.df['month'] = self.df['played_at'].dt.month
        self.df['day'] = self.df['played_at'].dt.day
        self.df['dayofweek'] = self.df['played_at'].dt.dayofweek # 0 = Monday, 6 = Sunday
        self.df['hour'] = self.df['played_at'].dt.hour

        self.df['month_sin'] = np.sin(2 * np.pi * self.df['month'] / 12)
        self.df['month_cos'] = np.cos(2 * np.pi * self.df['month'] / 12)
        self.df['dayofweek_sin'] = np.sin(2 * np.pi * self.df['dayofweek'] / 7)
        self.df['dayofweek_cos'] = np.cos(2 * np.pi * self.df['dayofweek'] / 7)
        self.df['day_sin'] = np.sin(2 * np.pi * self.df['day'] / 31)
        self.df['day_cos'] = np.cos(2 * np.pi * self.df['day'] / 31)

        return self
    
    def one_hot_multilabel_columns(self, columns):
        for col in columns:
            unique_values = self.df[col].str.split(', ').explode().dropna()
            unique_values = unique_values[unique_values != ''].unique().tolist()
            self.df[col] = self.df[col].fillna('').str.split(', ').apply(
                lambda x: pd.Series(unique_values).isin(x).astype(int).tolist()
            )
        return self

    def reduce_multilabel_columns(self, columns, n_components=1):
        for col in columns:
            mat = self.df[col].apply(pd.Series).fillna(0)

            pca = PCA(n_components=n_components)
            reduced = pd.DataFrame(
                pca.fit_transform(mat),
                index=self.df.index
            )

            if n_components == 1:
                self.df[col] = reduced.iloc[:, 0]
            else:
                reduced.columns = [f"{col}_{i+1}" for i in range(n_components)]
                self.df = pd.concat([self.df.drop(columns=[col]), reduced], axis=1)

        return self

    def vectorize_recent_tracks(self, n_components=1, played_at=False):
        """
        df : dataframe with last tracks (returned by get_recent_track)
        n_components : number of components used in the PCA method (integer)
        played_at : to get this feature in the resulting dataframe (Boolean)

        Return a dataframe with vectorized data
        """
        self.encode_ids(['album_id', 'track_id'])

        self.binarize_multilabel_column(['track_artists_id', 'album_artists_id'])

        self.vectorize_date(['release_date'])

        if played_at:
            self.add_played_at_features()

        self.one_hot_multilabel_columns(['similar_artists', 'track_tags'])
        self.reduce_multilabel_columns(
            ['similar_artists', 'track_tags', 'track_artists_id', 'album_artists_id'],
            n_components=n_components
        )

        return self.df

    ### TODO : Ecrire une fonction qui enlève toutes les colonnes inutiles du dataframe ou qui retient uniquement les colonnes vectorisées

    def scale_features(self, df):
        scaler = StandardScaler()
        return pd.DataFrame(
            scaler.fit_transform(df),
            columns=df.columns,
            index=df.index
        )

    def apply_weights(self, df, weights, n_components):
        if not weights:
            return df

        df_weighted = df.copy()
        for prefix, weight in weights.items():
            if prefix in df_weighted.columns:
                df_weighted[prefix] *= weight
            else:
                for i in range(1, n_components +1):
                    col_name = f"{prefix}_{i}" if n_components > 1 else prefix
                    if col_name in df_weighted.columns:
                        df_weighted[col_name] *= weight
        return df_weighted

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
    
    def run_pipeline(self):
        pass