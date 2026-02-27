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
        'noplaylist': False,
        'prefer_ffmpeg': True,
        'ignoreerrors': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
        except Exception as e:
            print(f"❌ Failed to download: {url}\nReason: {e}")
            return

        entries = info.get('entries', [info])
        if not entries:
            print("❌ No entries found.")
            return

        for entry in entries:
            if not entry:
                continue

            title = entry.get('title')
            if not title:
                continue

            audio_path = os.path.join(output_dir, f"{title}.{ext}")
            base_path_no_ext = os.path.splitext(audio_path)[0]
            thumb_webp = f"{base_path_no_ext}.webp"
            thumb_jpg = f"{base_path_no_ext}.jpg"

            if os.path.exists(thumb_webp) and not os.path.exists(thumb_jpg):
                converted = convert_webp_to_jpg(thumb_webp, thumb_jpg)
                if converted:
                    print(f"✅ Saved .jpg cover for: {title}")
                else:
                    print("❌ Thumbnail conversion failed.")
                try:
                    os.remove(thumb_webp)
                    print(f"[🧹] Deleted .webp: {thumb_webp}")
                except Exception as e:
                    print(f"⚠️ Couldn’t delete .webp: {e}")
            elif os.path.exists(thumb_jpg):
                print("⚠️ .jpg already exists for:", title)
            else:
                print("❌ No .webp thumbnail found for:", title)

def process_url_list(file_path, genre, ext, base_path):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    with open(file_path, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f"📄 Found {len(urls)} URLs in {file_path}\n")

    for idx, url in enumerate(urls, 1):
        print(f"\n🎵 [{idx}/{len(urls)}] Processing: {url}")
        download_audio(url, genre, ext, base_path)

    # Convert all remaining .webp files in the output folder recursively after downloads
    output_folder = os.path.join(base_path, ext, genre)
    convert_all_webp_in_folder(output_folder)

    print("\n✅ All downloads complete!")
    print("💽 Safely eject the drive before unplugging.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 5:
        print("Usage: python script.py <urls.txt path> <genre> <ext> <base download folder>")
    else:
        process_url_list(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
