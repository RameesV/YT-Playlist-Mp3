import os
from flask import Flask, render_template, request
import pytube

app = Flask(__name__)

def download_playlist(playlist_url, output_path=os.path.join(os.path.expanduser("~"), "Downloads/YouTube")):
    playlist = pytube.Playlist(playlist_url)
    print(f"Number of videos in playlist: {len(playlist.videos)}")

    count = 1
    for video in playlist.videos:
        try:
            audio_stream = video.streams.filter(only_audio=True).first()
            output_filename = f"{os.path.splitext(audio_stream.default_filename)[0]}.mp3"
            output_filepath = os.path.join(output_path, output_filename)
            audio_stream.download(output_path=output_path, filename=output_filename)
            print(f"{count} Downloaded: {output_filename}")
        except Exception as e:
            print(f"Error downloading {video.title}: {e}")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        playlist_url = request.form["playlist_url"]
        download_playlist(playlist_url)
    return render_template("index.html")

if __name__ == "__main__":
    app.run()
