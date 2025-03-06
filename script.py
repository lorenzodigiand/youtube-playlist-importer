import pandas as pd
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import os
import json
import time
from googleapiclient.errors import HttpError

def authenticate_youtube():
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "client_secret.json", scopes
    )
    credentials = flow.run_local_server(port=0)
    
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
    return youtube

def create_playlist(youtube, title="Spotify Import", description="Playlist importata da CSV"):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["music", "playlist"],
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": "public"
            }
        }
    )
    response = request.execute()
    return response["id"]

def search_video(youtube, query):
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=1
    )
    response = request.execute()
    time.sleep(1)  # Ritardo di 1 secondo per evitare superamento della quota
    if "items" in response and len(response["items"]) > 0:
        return response["items"][0]["id"]["videoId"]
    return None

def check_video_in_playlist(youtube, playlist_id, video_id):
    # Controlla se il video è già nella playlist
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id
    )
    response = request.execute()
    for item in response.get("items", []):
        if item["snippet"]["resourceId"]["videoId"] == video_id:
            return True
    return False

def add_video_to_playlist(youtube, playlist_id, video_id):
    retries = 5
    for attempt in range(retries):
        try:
            # Verifica se il video è già presente nella playlist
            if check_video_in_playlist(youtube, playlist_id, video_id):
                print(f"❌ Video già presente nella playlist: {video_id}")
                return

            # Se il video non è nella playlist, aggiungilo
            request = youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            )
            request.execute()
            print(f"✅ Video aggiunto con successo: {video_id}")
            break  # Esci dal ciclo se l'operazione ha successo
        except HttpError as e:
            if e.resp.status == 409:
                print(f"❌ Errore 409, tentativo {attempt + 1} di {retries}. Riprovo...")
                time.sleep(5)  # Attendi 5 secondi prima di riprovare
            else:
                print(f"❌ Errore imprevisto: {e}")
                break  # Se è un altro errore, interrompi il ciclo

def main():
    # Carica il CSV
    df = pd.read_csv("playlist.csv")
    
    # Controlla che le colonne esistano
    if not all(col in df.columns for col in ["Track name", "Artist name", "Album"]):
        print("❌ Errore: Il CSV deve contenere le colonne 'Track name', 'Artist name', 'Album'")
        return
    
    # Autenticazione con YouTube
    youtube = authenticate_youtube()
    
    # Crea una nuova playlist
    playlist_id = create_playlist(youtube)
    print(f"✅ Playlist creata con successo: https://www.youtube.com/playlist?list={playlist_id}")
    
    # Itera sulle canzoni e aggiungile alla playlist
    for index, row in df.iterrows():
        track = row["Track name"]
        artist = row["Artist name"]
        query = f"{track} {artist} official audio"
        
        video_id = search_video(youtube, query)
        if video_id:
            add_video_to_playlist(youtube, playlist_id, video_id)
            print(f"✅ Aggiunto: {track} - {artist}")
        else:
            print(f"❌ Non trovato: {track} - {artist}")
        
        # Ritardo tra le richieste per evitare di superare la quota
        time.sleep(1)
    
    print("🎵 Importazione completata!")

if __name__ == "__main__":
    main()
