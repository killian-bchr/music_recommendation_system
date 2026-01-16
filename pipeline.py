import logging
from pandas import DataFrame
from sqlalchemy.orm import Session

from database.crud import CRUD
from database.session import get_session
from preprocessing import DataBuilder, DataPreprocessor, DataTransformer, DataSelector
from helpers import DBHelpers, SpotifyHelpers

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(
        self,
        session: Session,
    ):
        self.session = session
    
    def load_listenings(self, nb_tracks: int = 10) -> None:
        logger.info("Extracting last listenings from Spotify...")
        items = SpotifyHelpers.extract_tracks(nb_tracks)
        listenings = DataBuilder.build_listenings(items)

        logger.info("Loading listenings to database...")
        CRUD.listenings_to_orm(self.session, listenings)
        CRUD.commit_session(self.session)

    def load_playlist(self, playlist_id: str) -> None:
        logger.info("Extracting tracks from a playlist...")
        playlist = DataBuilder.build_playlist(playlist_id)

        logger.info("Loading playlist to database...")
        CRUD.playlist_to_orm(self.session, playlist)
        CRUD.commit_session(self.session)

    def load_new_objects(self) -> None:
        logger.info("Fetching new Artists, Albums and Tracks from listenings...")
        new_artists = DataSelector.select_new_artists(self.session)
        new_albums = DataSelector.select_new_albums(self.session)
        new_tracks = DataSelector.select_new_tracks(self.session)

        logger.info("Loading new Artists, Albums and Tracks to database...")
        CRUD.albums_to_orm(self.session, new_albums)
        CRUD.artists_to_orm(self.session, new_artists)
        CRUD.tracks_to_orm(self.session, new_tracks)
        CRUD.commit_session(self.session)

    def transform_objects_to_df(self) -> tuple[DataFrame, DataFrame]:
        logger.info("Retrieving data from database...")
        all_tracks = DBHelpers.fetch_all_tracks(self.session)
        all_artists = DBHelpers.fetch_all_artists(self.session)

        logger.info("Transforming data to DataFrame...")
        tracks_df = DataTransformer.build_tracks_df(all_tracks)
        artists_df = DataTransformer.build_artists_df(all_artists)
        return tracks_df, artists_df

    def preprocess_data(self, tracks_df: DataFrame, artists_df: DataFrame) -> DataFrame:
        logger.info("Preprocessing...")
        return DataPreprocessor.vectorize_tracks(tracks_df, artists_df)

    def run_pipeline(self, nb_tracks: int = 10) -> DataFrame:
        logger.info("Starting pipeline...")

        self.load_listenings(nb_tracks)
        self.load_new_objects()
        tracks_df, artists_df = self.transform_objects_to_df()
        tracks_vectorized = self.preprocess_data(tracks_df, artists_df)

        logger.info(f"Pipeline completed - DataFrame shape: {tracks_vectorized.shape}")
        return tracks_vectorized

if __name__ == "__main__":
    with get_session() as session:
        pipeline = Pipeline(session)
        tracks_vectorized = pipeline.run_pipeline()
