from datetime import datetime
from typing import Dict

import numpy as np
import pandas as pd
from pandas import DataFrame, Series
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler

from settings.namming import ArtistColumns, TrackColumns


class DataPreprocessor:
    REFERENCE_DATE = datetime.strptime("01-01-2000", "%d-%m-%Y")

    @staticmethod
    def encode_date_column(column: Series) -> Series:
        column = pd.to_datetime(column, errors="coerce")
        column = column.fillna(DataPreprocessor.REFERENCE_DATE)
        return (column - DataPreprocessor.REFERENCE_DATE).dt.days

    @staticmethod
    def multihot_encode(column: Series, prefix: str) -> DataFrame:
        mlb = MultiLabelBinarizer()
        encoded = mlb.fit_transform(column)
        return DataFrame(
            encoded,
            columns=[f"{prefix}_{cls}" for cls in mlb.classes_],
            index=column.index,
        )

    @staticmethod
    def vectorize_artists(artists_df: DataFrame) -> DataFrame:
        tags_encoded = DataPreprocessor.multihot_encode(
            artists_df[ArtistColumns.TAGS], "tag"
        )
        similar_encoded = DataPreprocessor.multihot_encode(
            artists_df[ArtistColumns.SIMILAR_ARTISTS], "similar"
        )
        vectorized_df = pd.concat([tags_encoded, similar_encoded], axis=1)
        return vectorized_df

    @staticmethod
    def apply_svd_reduction(df: DataFrame, n_components: int = 80) -> DataFrame:
        if df.empty:
            return df

        svd = TruncatedSVD(
            n_components=min(n_components, df.shape[1] - 1), random_state=42
        )
        reduced_matrix = svd.fit_transform(df)

        reduced_df = DataFrame(
            reduced_matrix,
            columns=[f"svd_{i + 1}" for i in range(reduced_matrix.shape[1])],
            index=df.index,
        )

        return reduced_df

    @staticmethod
    def aggregate_artist_features(
        tracks_df: DataFrame, artists_df: DataFrame
    ) -> DataFrame:
        artist_features = artists_df.copy()

        aggregated_features = []
        for artist_list in tracks_df[TrackColumns.ARTIST_IDS]:
            artist_vectors = artist_features.loc[artist_list]
            mean_vector = artist_vectors.mean(axis=0).values
            max_vector = artist_vectors.max(axis=0).values
            std_vector = artist_vectors.std(axis=0).fillna(0).values

            combined_vector = np.concatenate([mean_vector, max_vector, std_vector])
            aggregated_features.append(combined_vector)

        artist_feature_names = []
        for agg_type in ["mean", "max", "std"]:
            artist_feature_names.extend(
                [f"artist_{agg_type}_{col}" for col in artist_features.columns]
            )

        artist_features_matrix = DataFrame(
            aggregated_features, columns=artist_feature_names, index=tracks_df.index
        )
        return artist_features_matrix

    @staticmethod
    def scale_features(df: DataFrame) -> DataFrame:
        scaler = StandardScaler()

        return DataFrame(scaler.fit_transform(df), columns=df.columns, index=df.index)

    @staticmethod
    def weight_features(df: DataFrame, weights: Dict[str, float] = None) -> DataFrame:
        default_weights = {
            TrackColumns.ALBUM_ID: 1.0,
            TrackColumns.RELEASE_DAYS: 1.0,
            TrackColumns.DURATION: 1.0,
            TrackColumns.POPULARITY: 1.0,
            TrackColumns.LISTENERS: 1.0,
            TrackColumns.PLAYCOUNT: 1.0,
        }

        if weights:
            default_weights.update(weights)

        for col, weight in default_weights.items():
            if col in df.columns:
                df[col] *= weight

        return df

    @staticmethod
    def vectorize_tracks(tracks_df: DataFrame, artists_df: DataFrame) -> DataFrame:
        tracks_processed = tracks_df.copy()

        tracks_processed[TrackColumns.RELEASE_DAYS] = (
            DataPreprocessor.encode_date_column(tracks_df[TrackColumns.RELEASE_DATE])
        )
        tracks_processed = tracks_processed.drop(columns=[TrackColumns.RELEASE_DATE])

        artists_vectorized = DataPreprocessor.vectorize_artists(artists_df)
        artists_reduced = DataPreprocessor.apply_svd_reduction(artists_vectorized)

        artist_features_matrix = DataPreprocessor.aggregate_artist_features(
            tracks_processed, artists_reduced
        )

        tracks_processed = pd.concat(
            [
                tracks_processed.drop(columns=[TrackColumns.ARTIST_IDS]),
                artist_features_matrix,
            ],
            axis=1,
        )

        final_df = tracks_processed.fillna(0)

        return DataPreprocessor.scale_features(final_df)
