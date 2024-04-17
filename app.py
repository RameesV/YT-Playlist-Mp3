import os
import re
from flask import Flask, render_template, request
from pytube import Playlist, YouTube
from moviepy.editor import VideoFileClip

app = Flask(__name__)

def clean_filename(filename):
    # Replace all characters other than English letters with space
    cleaned_filename = re.sub(r'[^a-zA-Z]+', ' ', filename)
    return cleaned_filename

def convert_to_mp3(input_file, output_file):
    try:
        video = VideoFileClip(input_file)
        audio = video.audio
        audio.write_audiofile(output_file, codec='mp3')
        print("Conversion completed successfully.")
    except Exception as e:
        print(f"Error converting video to MP3: {e}")
    finally:
        video.close()  # Close the video clip after conversion

def download_playlist(playlist_url, output_path=os.path.join(os.path.expanduser("~"), "Downloads/YouTube")):
    playlist = Playlist(playlist_url)
    print(f"\n{'*'*40}\n*** Number of videos in playlist: {len(playlist.video_urls)} ***\n{'*'*40}")

    count = 0
    total_videos = len(playlist.video_urls)
    for video_url in playlist.video_urls:
        try:
            video = YouTube(video_url)
            video_stream = video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first() or video.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
            # audio_stream = video.streams.filter(only_audio=True, file_extension='mp3').order_by('abr').desc().first()
            
            if video_stream:
                video_title = clean_filename(video.title)
                video_filename = f"{video_title}.mp4"
                audio_filename = f"{video_title}.mp3"
                
                video_stream.download(output_path=output_path, filename=video_filename)
                convert_to_mp3(os.path.join(output_path, video_filename), os.path.join(output_path, audio_filename))
                count += 1
                percentage_complete = (count / total_videos) * 100
                print(f"\n_______________________________\n|| {count}/{total_videos} || ({percentage_complete:.2f}%) || Converted: {video_filename}\n===============================")

                # Try deleting the video file only if conversion is successful
                try:
                    os.remove(os.path.join(output_path, video_filename))
                    print(f"Deleted video file: {video_filename}")
                except OSError as e:
                    print(f"Error deleting video file: {video_filename} - {e}")
            
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
    app.run(port=5001)
