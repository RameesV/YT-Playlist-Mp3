import os
from flask import Flask, render_template, request
from pytube import Playlist
from pytube import YouTube
from moviepy.editor import VideoFileClip
import re

app = Flask(__name__)

def clean_filename(filename):
    # Remove non-English characters
    cleaned_filename = re.sub(r'[^a-zA-Z]+', ' ', filename)
    return cleaned_filename

def download_playlist(playlist_url, output_path=os.path.join(os.path.expanduser("~"), "Downloads/YouTube")):
    playlist = Playlist(playlist_url)
    print(f"\n{'*'*40}\n*** Number of videos in playlist: {len(playlist.video_urls)} ***\n{'*'*40}")

    count = 0
    total_videos = len(playlist.video_urls)
    for video_url in playlist.video_urls:
        try:
            video = YouTube(video_url)
            video_stream = video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first() or video.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
            audio_stream = video.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc().first()
            
            if video_stream and audio_stream:
                # Clean and truncate the filename
                video_title = clean_filename(video.title)
                video_filename = f"{video_title}.mp4"
                audio_filename = f"{video_title}_audio.mp4"
                
                # Check if filename is empty
                if not video_title:
                    video_filename = f"songs_{count}.mp4"
                    audio_filename = f"songs_{count}_audio.mp4"
                
                video_stream.download(output_path=output_path, filename=video_filename)
                audio_stream.download(output_path=output_path, filename=audio_filename)
                count += 1
                percentage_complete = (count / total_videos) * 100
                print(f"{count}/{total_videos} ({percentage_complete:.2f}%) Downloaded: {video.title}")
            else:
                print(f"No suitable streams found for {video.title}")
        except Exception as e:
            print(f"Error downloading {video_url}: {e}")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        playlist_url = request.form["playlist_url"]
        download_playlist(playlist_url)
    return render_template("index.html")

if __name__ == "__main__":
    app.run()
