import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import warnings
from kneed import KneeLocator
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer

from authentication import spotify_client as sp
from engine.utils.lastfmclient import LastFMClient


class Helpers:

    @staticmethod
    def get_artist_details(artist: str, method: str) -> dict:
        params = {
            'method': method,
            'artist': artist,
        }
        return LastFMClient.make_lastfm_request(params)


    @staticmethod
    def get_track_details(track: str, artist: str, method: str) -> dict:
        params = {
            'method': method,
            'artist': artist,
            'track': track,
        }
        return LastFMClient.make_lastfm_request(params)

    ### Spotify functions
    @staticmethod
    def search_track(track_name: str, artist_name: str = None):
        """
        track_name : track name (string)
        artist_name : atist name (string)

        Return a dictionnaire containing all track's features
        """

        query = f"track:{track_name}"
        if artist_name:
            query += f" artist:{artist_name}"

        results = sp.search(q=query, type="track", limit=1)

        if results["tracks"]["items"]:
            track = results["tracks"]["items"][0]

            album_images = track["album"]["images"]
            album_image_url = album_images[1]["url"] if len(album_images) > 1 else album_images[0]["url"]
            
            return {
                "album_id": track["album"]["id"],
                "album_name": track["album"]["name"],
                "release_date": track["album"]["release_date"],
                "album_artists_id": ", ".join(str(artist["id"]) for artist in track["album"]["artists"]),
                "album_artists_name": ", ".join(artist["name"] for artist in track["album"]["artists"]),
                "duration": track['duration_ms']/1000,
                "track_id": track["id"],
                "track_name": track["name"],
                "popularity": track["popularity"],
                "track_artists_id": ", ".join(str(artist["id"]) for artist in track["artists"]),
                "track_artists_name": ", ".join(artist["name"] for artist in track["artists"]),
                'image_url': album_image_url,
                'spotify_url': track['external_urls']['spotify']
            }
        else:
            return None
        
    @staticmethod
    def get_playlist_tracks(playlist_id):
        """
        playlist_id : id of a playlist (string)
        
        Return a dataframe with all playlist's tracks
        """

        tracks = []
        # We create an offset because the API request is limited to 100 tracks
        offset = 0

        while True:
            response = sp.playlist_tracks(playlist_id, limit=100, offset=offset)
            items = response.get('items', [])
            
            for item in items:
                track = item['track']
                album_images = track['album']['images']
                album_image_url = album_images[1]['url'] if len(album_images) > 1 else album_images[0]['url']

                track_details = Utils.get_track_details(
                    track=track['name'], 
                    artist=track['artists'][0]['name'],
                    method='track.getInfo'
                ) or {}

                track_details = track_details.get('track', {})

                similar_artists_list = []
                track_tags_list = []

                for artist in track['artists']:
                    current_artist = artist['name']
                    artist_details = Utils.get_artist_details(
                        artist=current_artist,
                        method='artist.getInfo'
                    ) or {}

                    if "error" not in artist_details:
                        similar_artists = artist_details.get('artist', {}).get('similar', {}).get('artist', [])
                        similar_artists_list.extend([similar_artist['name'] for similar_artist in similar_artists])

                        tags = artist_details.get('artist', {}).get('tags', {}).get('tag', [])
                        track_tags_list.extend([tag['name'] for tag in tags])
                
                similar_artists_str = ", ".join(set(similar_artists_list))
                track_tags_str = ", ".join(set(track_tags_list))

                tracks.append({
                    'album_id': track['album']['id'],
                    'album_name': track['album']['name'],
                    'release_date': track['album']['release_date'],
                    'album_artists_id': ', '.join([artist['id'] for artist in track['album']['artists']]),
                    'album_artists_name': ', '.join([artist['name'] for artist in track['album']['artists']]),
                    'duration': track['duration_ms']/1000,
                    'track_id': track['id'],
                    'track_name': track['name'],
                    'popularity': track['popularity'],
                    'track_artists_id': ', '.join([artist['id'] for artist in track['artists']]),
                    'track_artists_name': ', '.join([artist['name'] for artist in track['artists']]),
                    'track_listeners': track_details.get('listeners', np.nan),
                    'track_playcount': track_details.get('playcount', np.nan),
                    'similar_artists': similar_artists_str,
                    'track_tags': track_tags_str,
                    'image_url': album_image_url,
                    'spotify_url': track['external_urls']['spotify']
                })
                    
            
            if len(items) < 100:
                break

            offset += 100

        playlist = pd.DataFrame(tracks)
        playlist['release_date'] = pd.to_datetime(playlist['release_date'], errors='coerce')

        return playlist
    
    @staticmethod
    def get_recent_tracks(numbers):
        """
        numbers : number of last tracks you want to get (must be <50 because we can't load more than 50) (integer)

        Return a dataframe with the last tracks listened and further informations for each one
        """

        limit = min(50, numbers)
        response = sp.current_user_recently_played(limit=limit)
        items = response.get('items', [])

        all_tracks = []

        for item in items:
            track = item['track']
            album_images = track['album']['images']
            album_image_url = album_images[1]['url'] if len(album_images) > 1 else album_images[0]['url']

            track_details = Utils.get_track_details(
                track=track['name'],
                artist=track['artists'][0]['name'],
                method='track.getInfo'
            ) or {}

            track_details = track_details.get('track', {})

            similar_artists_list = []
            track_tags_list = []

            for artist in track['artists']:
                current_artist = artist['name']
                artist_details = Utils.get_artist_details(
                    artist=current_artist,
                    method='artist.getInfo'
                ) or {}

                if "error" not in artist_details:
                    similar_artists = artist_details.get('artist', {}).get('similar', {}).get('artist', [])
                    similar_artists_list.extend([similar_artist['name'] for similar_artist in similar_artists])

            tags = artist_details.get('artist', {}).get('tags', {}).get('tag', [])
            track_tags_list.extend([tag['name'] for tag in tags])
                    
            similar_artists_str = ", ".join(set(similar_artists_list))
            track_tags_str = ", ".join(set(track_tags_list))

            all_tracks.append({
                'album_id': track['album']['id'],
                'album_name': track['album']['name'],
                'release_date': track['album']['release_date'],
                'album_artists_id': ', '.join([artist['id'] for artist in track['album']['artists']]),
                'album_artists_name': ', '.join([artist['name'] for artist in track['album']['artists']]),
                'duration': track['duration_ms']/1000,
                'track_id': track['id'],
                'track_name': track['name'],
                'popularity': track['popularity'],
                'track_artists_id': ', '.join([artist['id'] for artist in track['artists']]),
                'track_artists_name': ', '.join([artist['name'] for artist in track['artists']]),
                'track_listeners': track_details.get('listeners', np.nan),
                'track_playcount': track_details.get('playcount', np.nan),
                'similar_artists': similar_artists_str,
                'played_at':item['played_at'],
                'track_tags': track_tags_str,
                'image_url': album_image_url,
                'spotify_url': track['external_urls']['spotify']
            })

        recent_tracks_df = pd.DataFrame(all_tracks)
        recent_tracks_df.reset_index(inplace=True, drop=True)
        recent_tracks_df['release_date'] = pd.to_datetime(recent_tracks_df['release_date'], errors='coerce')
        recent_tracks_df['played_at'] = pd.to_datetime(recent_tracks_df['played_at'], errors='coerce')
        return recent_tracks_df

    @staticmethod
    def remove_outliers(df):
        for column in df.columns:
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

    ### Clustering

    ### Using K-Means
    @staticmethod
    def clustering(tracklist):
        """
        tracklist : vectorized and scaled features of a trakclist

        Return a Series with the same index as vectorized, scaled and weighted data containing the respective cluster for each track
        """
        tracklist = tracklist.copy()
        tracklist.columns = tracklist.columns.astype(str)
        tracklist.drop(columns=['track_id'], inplace=True, errors='ignore')

        ### Pour éviter d'utiliser dropna et garder le même nombre de lignes
        imputer = SimpleImputer(strategy="mean")
        tracklist_imputed = pd.DataFrame(imputer.fit_transform(tracklist), columns=tracklist.columns)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            inertia = []
            K_range = range(2, 11)
            for k in K_range:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                kmeans.fit(tracklist_imputed)
                inertia.append(kmeans.inertia_)

            knee = KneeLocator(K_range, inertia, curve="convex", direction="decreasing")
            optimal_k = knee.knee

            if optimal_k is None:
                optimal_k = 2

            kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)

            return kmeans.fit_predict(tracklist_imputed)

    @staticmethod
    def visualize_clustering(tracklist, feature=None):
        """
        tracklist : vectorized and scaled features of a trakclist
        feature : a feature you want to be displayed when you hover the point on the scatter plot
                example of feature : tracklist[['track_name']] --> display the track_name when you hover the point on the scatter plot

        Display a scatter plot of the clustering
        """
        tracklist = tracklist.copy()
        tracklist.columns = tracklist.columns.astype(str)
        tracklist.drop(columns=['track_id'], inplace=True, errors='ignore')

        ### Pour éviter d'utiliser dropna et garder le même nombre de lignes
        imputer = SimpleImputer(strategy="mean")
        tracklist_imputed = pd.DataFrame(imputer.fit_transform(tracklist), columns=tracklist.columns)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            inertia = []
            K_range = range(2, 11)
            for k in K_range:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                kmeans.fit(tracklist_imputed)
                inertia.append(kmeans.inertia_)

            plt.plot(K_range, inertia, marker='o')
            plt.title("Méthode du coude pour déterminer le nombre optimal de clusters")
            plt.xlabel("Nombre de clusters")
            plt.ylabel("Inertie")
            plt.show()

            knee = KneeLocator(K_range, inertia, curve="convex", direction="decreasing")
            optimal_k = knee.knee

            if optimal_k is None:
                optimal_k = 2

            optimal_k = 4  ## juste pour tester avec un nombre de cluster précis

            kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)

            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(tracklist_imputed)

            df_pca = pd.DataFrame(X_pca, columns=['PCA1', 'PCA2'])
            df_pca['Cluster'] = kmeans.fit_predict(tracklist_imputed)

            if feature is not None:
                df_pca['Track_ID'] = feature
            else:
                df_pca['Track_ID'] = pd.Series()

            fig = px.scatter(df_pca, x='PCA1', y='PCA2', color='Cluster', hover_data={'Track_ID': True, 'PCA1': True, 'PCA2': True})
            fig.update_layout(title="Clustering (PCA Projection)", title_x=0.5)
            fig.show()

    
    ### Get clusters
    @staticmethod
    def get_tracklist_clust(tracklist):
        """
        tracklist: tracklist vectorized and scaled

        Return tracklist with the column "cluster" resulting from clustering
        """
        cluster = Utils.clustering(tracklist)
        tracklist['cluster'] = cluster
        return tracklist


    @staticmethod
    def get_clusters(tracklist_clust, limit=3):
        """"
        tracklist_clust: dataframe of recent tracks listened with column 'cluster' after clustering
        limit: limit for similar songs (to reduce execution time)

        Return a dictionnary of tracklist's dataframes for each cluster
        """
        tracklist_clust = tracklist_clust.copy()
        n_clusters = tracklist_clust['cluster'].nunique()
        cluster_dfs = {}

        for i in range(n_clusters):
            cluster = tracklist_clust[tracklist_clust['cluster']==i].copy()
            cluster = cluster[['album_id', 'album_name', 'release_date', 'album_artists_id', 'album_artists_name', 'duration',
                    'track_id', 'track_name', 'popularity', 'track_artists_id', 'track_artists_name',
                    'track_listeners', 'track_playcount', 'similar_artists', 'track_tags']]
            l=len(cluster)

            for j in range(l):

                similar_tracks = Utils.get_track_details(
                    track = cluster['track_name'].iloc[j],
                    artist = cluster['track_artists_name'].iloc[j].split(",")[0], 
                    api_key = api_key, 
                    method = 'track.getSimilar'
                )

                if "error" not in similar_tracks:
                    similar_tracks = similar_tracks.get('similartracks', {}).get('track', {})[:limit]
                    for track in similar_tracks:
                        new_track = pd.json_normalize(Utils.search_track(track['name'], track['artist']['name']))
                        new_track.drop(columns=['image_url', 'spotify_url'], inplace=True, errors='ignore')
                        new_track_details = Utils.get_track_details(
                            track = track['name'], 
                            artist = track['artist']['name'], 
                            api_key = api_key, 
                            method = 'track.getInfo'
                        )

                        if "error" in new_track_details:
                            new_track_details_df = pd.DataFrame(columns=['track_listeners', 'track_playcount'])
                        else:
                            new_track_details_df = pd.json_normalize(new_track_details.get('track', {})).get(['listeners', 'playcount'], pd.DataFrame())
                            new_track_details_df.rename(columns={'listeners': 'track_listeners', 'playcount': 'track_playcount'}, inplace=True)
                        
                        similar_artists_list = []
                        track_tags_list = []

                        artist_details = Utils.get_artist_details(
                                                artist=track['artist']['name'],
                                                api_key=api_key,
                                                method='artist.getInfo'
                                            )

                        if "error" in artist_details:
                            similar_artists_list.append(None)
                        else:
                            similar_artists = artist_details.get('artist', {}).get('similar', {}).get('artist', [])
                            similar_artists_list.extend([similar_artist['name'] for similar_artist in similar_artists])

                        if "error" in artist_details:
                            track_tags_list.append(None)
                        else:
                            tags = artist_details.get('artist', {}).get('tags', {}).get('tag', [])
                            track_tags_list.extend([tag['name'] for tag in tags])
                                
                        similar_artists_str = ", ".join([artist for artist in set(similar_artists_list) if artist is not None])     # Use of set in order to avoid duplicates
                        track_tags_str = ", ".join([track for track in set(track_tags_list) if track is not None])      # Use of set in order to avoid duplicates

                        new_track_details_df['similar_artists'] = similar_artists_str
                        new_track_details_df['track_tags'] = track_tags_str

                        new_track = pd.concat([new_track, new_track_details_df], axis=1)

                        if not new_track.empty:
                            cluster = pd.concat([cluster, new_track], axis=0)
                
            cluster.drop_duplicates(subset=['track_name'], inplace=True)
            cluster['release_date'] = pd.to_datetime(cluster['release_date'], errors='coerce')
            cluster.reset_index(drop=True, inplace=True)
                
            cluster_dfs[i] = cluster if not cluster.empty else pd.DataFrame()

        return cluster_dfs

    @staticmethod
    def search_similar_tracks_by_pos(tracklist, clusters, cosine_matrices, track_pos, nb_tracks=5):
        track = tracklist.iloc[track_pos]
        num_cluster = track['cluster']

        cluster = clusters[num_cluster]
        cosine_sim_matrix = cosine_matrices[num_cluster]

        # Trouver la position du track dans le cluster
        current_cluster = tracklist[tracklist['cluster'] == num_cluster].reset_index(drop=True)
        new_track_pos = current_cluster[current_cluster['track_name'] == track['track_name']].index[0]

        # Calcul des similarités
        similarities = list(enumerate(cosine_sim_matrix[new_track_pos]))
        similarities = sorted(similarities, key=lambda x: x[1], reverse=True)

        # Sélection des tracks les plus proches (hors track lui-même)
        top_similar_tracks = [cluster.iloc[i[0]]['track_name'] for i in similarities[1:nb_tracks+1] if i[0] < len(cluster)]
        top_similar_tracks = list(dict.fromkeys(top_similar_tracks))
        top_similar_tracks_str = ", ".join(top_similar_tracks)

        return f"Tracks similaires à '{track['track_name']}' : {top_similar_tracks_str}"
    
    @staticmethod
    def search_similar_tracks_by_name(tracklist, clusters, cosine_matrices, track_name, nb_tracks=5):
        filtered_tracks = tracklist[tracklist['track_name'] == track_name]
        if not filtered_tracks.empty:
            track = filtered_tracks.iloc[0]
        else:
            return f"Aucun morceau trouvé avec le nom '{track_name}'"

        num_cluster = track['cluster']

        cluster = clusters[num_cluster]
        cosine_sim_matrix = cosine_matrices[num_cluster]

        # Trouver la position du track dans le cluster
        current_cluster = tracklist[tracklist['cluster'] == num_cluster].reset_index(drop=True)
        new_track_pos = current_cluster[current_cluster['track_name'] == track['track_name']].index[0]

        # Calcul des similarités
        similarities = list(enumerate(cosine_sim_matrix[new_track_pos]))
        similarities = sorted(similarities, key=lambda x: x[1], reverse=True)

        # Sélection des tracks les plus proches (hors track lui-même)
        top_similar_tracks = [cluster.iloc[i[0]]['track_name'] for i in similarities[1:nb_tracks+1] if i[0] < len(cluster)]
        top_similar_tracks = list(dict.fromkeys(top_similar_tracks))

        return top_similar_tracks
