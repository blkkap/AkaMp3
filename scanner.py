import os
import subprocess
import glob

def convert_all_webp_in_folder(root_dir):
    # Find all .webp files recursively
    webp_files = glob.glob(os.path.join(root_dir, '**', '*.webp'), recursive=True)

    print(f"🔍 Found {len(webp_files)} .webp file(s) in {root_dir}\n")

    for webp_path in webp_files:
        jpg_path = os.path.splitext(webp_path)[0] + '.jpg'

        print(f"🖼️ Converting and resizing: {webp_path} → {jpg_path}")
        result = subprocess.run([
            'ffmpeg', '-y',
            '-i', webp_path,
            '-vf', 'scale=300:300',         # Resize to 300x300
            '-q:v', '2',                    # Good quality JPEG
            '-pix_fmt', 'yuvj420p',         # Rockbox-safe pixel format
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

if __name__ == "__main__":
    # Example usage, change path as needed
    convert_all_webp_in_folder("/Volumes/DJHAGRID/mu$ick/flac/rap/")
