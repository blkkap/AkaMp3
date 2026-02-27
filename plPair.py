import os
import shutil
import subprocess

def organize_album_into_folder(source_folder, album_name, file_ext=".m4a"):
    album_folder = os.path.join(source_folder, album_name)
    os.makedirs(album_folder, exist_ok=True)

    files = os.listdir(source_folder)
    audio_files = [f for f in files if f.lower().endswith(file_ext.lower())]

    print(f"🔍 Found {len(audio_files)} {file_ext} files to organize into album folder: {album_name}\n")

    for audio_file in audio_files:
        base_name = os.path.splitext(audio_file)[0]
        jpg_file = base_name + ".jpg"

        audio_path = os.path.join(source_folder, audio_file)
        jpg_path = os.path.join(source_folder, jpg_file)

        if not os.path.exists(jpg_path):
            print(f"⚠️ Skipping: No matching JPG for {audio_file}")
            continue

        new_audio_path = os.path.join(album_folder, audio_file)
        new_cover_path = os.path.join(album_folder, base_name + "_cover.jpg")

        shutil.move(audio_path, new_audio_path)

        result = subprocess.run([
            'ffmpeg', '-y',
            '-i', jpg_path,
            '-vf', 'scale=300:-1',
            '-q:v', '2',
            '-pix_fmt', 'yuvj420p',
            '-colorspace', 'bt470bg',
            new_cover_path
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Moved & converted: {base_name}")
            os.remove(jpg_path)
        else:
            print(f"❌ ffmpeg error for: {jpg_file}")
            print(result.stderr)

    print(f"\n🎉 Done! All songs are now in: {album_folder}")

if __name__ == "__main__":
    # Example usage with .flac files
    organize_album_into_folder("/Volumes/DJHAGRID/mu$ick/flac/rap/", "Let God Sort Em Out - Clipse, Pusha T & Malice", ".flac")
