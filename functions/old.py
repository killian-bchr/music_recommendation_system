def search_similar_tracks_all(df, track_pos, nb_tracks=5, n_components=1, limit=3):
    ### Clustering
    df_vect = vectorize_recent_tracks(df, n_components)
    df['cluster'] = clustering(df_vect)

    cluster_dfs = get_tracklist(df, limit=limit)
    cluster_dfs_vect = vectorize_tracklist(cluster_dfs)

    ### Retrieve the track in the dataframe
    track = df.iloc[track_pos]
    ### Retrieve the track's cluster
    num_cluster = track['cluster']

    ### Get the right cluster
    cluster = cluster_dfs_vect[num_cluster]
    
    ## Récupérer la nouvelle position du track dans le cluster
    current_cluster = df[df['cluster'] == num_cluster].reset_index(drop=True)
    new_track_pos = current_cluster[current_cluster['track_name'] == track['track_name']].index[0]

    ### Get the cosine matrix
    cosine_sim_matrix = cosine_similarity(cluster.fillna(0))  ### Utilisation de fillna pour garder le même nombre de lignes (et ainsi les mêmes positions(track_pos))

    similarities = list(enumerate(cosine_sim_matrix[new_track_pos]))  # on cherche pour la position du track souhaité
    similarities = sorted(similarities, key=lambda x: x[1], reverse=True)  # Trier par similarité décroissante

    # Récupérer les indices des 5 tracks les plus proches (en excluant le track lui-même)
    top_similar_tracks = [cluster_dfs[num_cluster].iloc[i[0]]['track_name'] for i in similarities[1:nb_tracks+1]if i[0] < len(cluster_dfs[num_cluster])]
    top_similar_tracks = list(dict.fromkeys(top_similar_tracks))
    top_similar_tracks_str = ", ".join(top_similar_tracks)

    return f"Tracks similaires à '{track['track_name']}' : {top_similar_tracks_str}"