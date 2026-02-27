import os
import subprocess
import glob
from yt_dlp import YoutubeDL

def convert_all_webp_in_folder(root_dir):
    webp_files = glob.glob(os.path.join(root_dir, '**', '*.webp'), recursive=True)
    print(f"🔍 Found {len(webp_files)} .webp file(s) in {root_dir}\n")

    for webp_path in webp_files:
        jpg_path = os.path.splitext(webp_path)[0] + '.jpg'
        print(f"🖼️ Converting and resizing: {webp_path} → {jpg_path}")
        result = subprocess.run([
            'ffmpeg', '-y',
            '-i', webp_path,
            '-vf', 'scale=300:300',
            '-q:v', '2',
            '-pix_fmt', 'yuvj420p',
            jpg_path
        ], capture_output=True, text=True)

        if result.returncode == 0 and os.path.exists(jpg_path):
            try:
                os.remove(webp_path)
                print(f"✅ Converted, resized, and deleted: {webp_path}")
            except Exception as e:
                print(f"⚠️ Error deleting {webp_path}: {e}")
        else:
            print(f"❌ Failed to convert {webp_path}")
            print(result.stderr)

    print("\n🎉 All done resizing JPGs to 300x300 for Rockbox.")

def convert_webp_to_jpg(webp_path, jpg_path):
    if not os.path.exists(webp_path):
        print(f"❌ WebP thumbnail not found: {webp_path}")
        return False

    print(f"[📷] Converting {webp_path} → {jpg_path}")
    result = subprocess.run([
        'ffmpeg', '-y',
        '-i', webp_path,
        '-vf', 'scale=300:300',
        '-q:v', '2',
        '-pix_fmt', 'yuvj420p',
        jpg_path
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ ffmpeg failed to convert webp to jpg:")
        print(result.stderr)
        return False

    return os.path.exists(jpg_path)

def create_output_folder(base_path, ext, genre):
    folder = os.path.join(base_path, ext, genre)
    os.makedirs(folder, exist_ok=True)
    return folder

def download_audio(url, genre, ext, base_path):
    output_dir = create_output_folder(base_path, ext, genre)

    # Use title as subfolder, we'll move things there later
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'writethumbnail': True,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': ext,
                'preferredquality': '192',
            },
            {
                'key': 'FFmpegMetadata',
            },
        ],
        'embedthumbnail': False,
        'addmetadata': True,
        'quiet': False,
        'noplaylist': True,
        'prefer_ffmpeg': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
        except Exception as e:
            print(f"❌ Failed to download: {url}\nReason: {e}")
            return

    # Locate audio file
    title = info.get("title")
    base_audio_path = os.path.join(output_dir, f"{title}.{ext}")
    webp_path = os.path.join(output_dir, f"{title}.webp")
    cover_jpg_path = os.path.join(output_dir, f"{title}.jpg")

    if not os.path.exists(base_audio_path):
        print(f"❌ No audio file found: {base_audio_path}")
        return

    # Create folder for this song
    song_folder = os.path.join(output_dir, title)
    os.makedirs(song_folder, exist_ok=True)

    # Move the audio file into the song folder
    new_audio_path = os.path.join(song_folder, f"{title}.{ext}")
    os.rename(base_audio_path, new_audio_path)

    # Convert webp to cover.jpg and move
    if os.path.exists(webp_path):
        temp_jpg_path = os.path.join(output_dir, f"{title}.jpg")
        convert_webp_to_jpg(webp_path, temp_jpg_path)

        final_cover_path = os.path.join(song_folder, "cover.jpg")
        os.rename(temp_jpg_path, final_cover_path)

        try:
            os.remove(webp_path)
            print(f"[🧹] Deleted original .webp: {webp_path}")
        except Exception as e:
            print(f"⚠️ Couldn't delete {webp_path}: {e}")
    else:
        print("❌ No .webp thumbnail found.")

    print(f"✅ Finished: {title}")


def process_url_list(file_path, genre, ext, base_path):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    with open(file_path, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f"📄 Found {len(urls)} URLs in {file_path}\n")

    for idx, url in enumerate(urls, 1):
        print(f"\n🎵 [{idx}/{len(urls)}] Downloading: {url}")
        download_audio(url, genre, ext, base_path)

    # Convert all remaining .webp files in the output folder recursively after downloads
    output_folder = os.path.join(base_path, ext, genre)
    convert_all_webp_in_folder(output_folder)

    print("\n✅ All downloads complete!")
    print("💽 Safely eject your drive before unplugging.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download music and convert thumbnails")
    parser.add_argument("--urlfile", required=True, help="Path to the urls.txt file")
    parser.add_argument("--genre", required=True, help="Genre folder name")
    parser.add_argument("--ext", default="flac", help="Audio format extension (flac, m4a, mp3)")
    parser.add_argument("--output", required=True, help="Base output directory")

    args = parser.parse_args()

    process_url_list(args.urlfile, args.genre, args.ext.lower(), args.output)
