import os
import shutil
import subprocess

def organize_album_files(base_output_folder, music_ext, genre, file_ext=".m4a"):
    """
    Organize files by creating a folder for each song using its filename (without extension),
    then move the song and its matching JPG cover inside that folder.

    Folder structure:
    base_output_folder/music_ext/genre/[song_name]/songfile + jpg

    Args:
        base_output_folder (str): Base folder chosen by user.
        music_ext (str): Extension folder (e.g., "m4a", "flac").
        genre (str): Genre folder name (e.g., "rap").
        file_ext (str): Audio file extension to look for (default ".m4a").
    """

    # Folder where the files are downloaded flat
    source_folder = os.path.join(base_output_folder, music_ext, genre)

    files = os.listdir(source_folder)
    audio_files = [f for f in files if f.lower().endswith(file_ext.lower())]

    print(f"🔍 Found {len(audio_files)} {file_ext} files to organize into individual folders in {source_folder}\n")

    for audio_file in audio_files:
        base_name = os.path.splitext(audio_file)[0]
        jpg_file = base_name + ".jpg"

        audio_path = os.path.join(source_folder, audio_file)
        jpg_path = os.path.join(source_folder, jpg_file)

        # Create a folder named after the song (base_name)
        song_folder = os.path.join(source_folder, base_name)
        os.makedirs(song_folder, exist_ok=True)

        new_audio_path = os.path.join(song_folder, audio_file)
        new_cover_path = os.path.join(song_folder, f"{base_name}_cover.jpg")

        # Move audio file into its folder
        shutil.move(audio_path, new_audio_path)

        if os.path.exists(jpg_path):
            # Convert and move the jpg cover
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
                print(f"✅ Moved & converted cover: {base_name}")
                os.remove(jpg_path)
            else:
                print(f"❌ ffmpeg error for: {jpg_file}")
                print(result.stderr)
        else:
            print(f"⚠️ No matching JPG for {audio_file}")

    print(f"\n🎉 Done! All songs have been moved into their own folders in {source_folder}")

if __name__ == "__main__":
    base_output = "/Volumes/DJHAGRID/mu$ick"
    ext = "m4a"
    genre = "rap"

    organize_album_files(base_output, ext, genre, f".{ext}")
