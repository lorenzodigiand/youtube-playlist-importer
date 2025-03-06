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

def create_playlist(youtube, title="Spotify Import", description="Playlist imported from CSV"):
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
    time.sleep(1)  # Delay of 1 second to circumvent the surpassing of the daily quota
    if "items" in response and len(response["items"]) > 0:
        return response["items"][0]["id"]["videoId"]
    return None

def check_video_in_playlist(youtube, playlist_id, video_id):
    # Check if the video is already in the playlist
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
            # Verify if the video is already in the playlist
            if check_video_in_playlist(youtube, playlist_id, video_id):
                print(f"❌ Track is already in the playlist: {video_id}")
                return

            # If the video is not found in the playlist, add it
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
            print(f"✅ Track added successfully: {video_id}")
            break  # Exit from the loop if the operation was successful
        except HttpError as e:
            if e.resp.status == 409:
                print(f"❌ Error 409, attempt number {attempt + 1} of {retries}. Trying again...")
                time.sleep(5)  # Wait 5 seconds before trying again
            else:
                print(f"❌ Unexpected error: {e}")
                break  # If it's another error, exit from the loop

def main():
    # Load CSV file
    df = pd.read_csv("playlist.csv")
    
    # Check if the columns exist
    if not all(col in df.columns for col in ["Track name", "Artist name", "Album"]):
        print("❌ Error: CSV must contain the columns 'Track name', 'Artist name', 'Album'")
        return
    
    # YouTube authentication
    youtube = authenticate_youtube()

    # Create a new playlist
    playlist_id = create_playlist(youtube)
    print(f"✅ Playlist created successfully: https://www.youtube.com/playlist?list={playlist_id}")
    
    # Cycle on the tracks and adds them to the playlist
    for index, row in df.iterrows():
        track = row["Track name"]
        artist = row["Artist name"]
        query = f"{track} {artist} official audio"
        
        video_id = search_video(youtube, query)
        if video_id:
            add_video_to_playlist(youtube, playlist_id, video_id)
            print(f"✅ Added: {track} - {artist}")
        else:
            print(f"❌ Not found: {track} - {artist}")
        
        # Delay between requests to circumvent the surpassing of the daily quota
        time.sleep(1)
    
    print("🎵 Import completed!")

if __name__ == "__main__":
    main()
