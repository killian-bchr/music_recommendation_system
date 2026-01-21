from database.db_env import DBEnv
from database.session import get_session
from database.tables import TrackORM
from helpers import DBHelpers
from recommendation_engine.services import MarkovRecommender
from settings.constants import MarkovStrategy, RandomWalkStrategy


class Service:
    @staticmethod
    def fetch_recent_tracks(
        n_listenings: int = 5,
        env: DBEnv = DBEnv.EXP,
    ) -> TrackORM:
        with get_session(env) as session:
            last_tracks = DBHelpers.fetch_last_tracks_listened(session, n_listenings)
        return last_tracks

    @staticmethod
    def fetch_recommended_tracks(
        markov_strategy: MarkovStrategy = MarkovStrategy.BALANCED,
        walk_strategy: RandomWalkStrategy = RandomWalkStrategy.POWER_ITERATION,
        n_last_listenings: int = 1,
        top_k: int = 5,
        env: DBEnv = DBEnv.EXP,
    ):
        recommender = MarkovRecommender(
            markov_strategy,
            walk_strategy,
            n_last_listenings,
            env,
        )

        recommendations = recommender.recommend(top_k)
        with get_session(env) as session:
            tracks = DBHelpers.get_tracks_by_ids(session, recommendations)

        return tracks
