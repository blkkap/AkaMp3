import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading

# Import your modules
import ytdl
import playList
import pairDIR
import plPair

# GUI Setup
root = tk.Tk()
root.title("AkaMp3")

# Variables
url_path_var = tk.StringVar()
output_path_var = tk.StringVar()
genre_var = tk.StringVar(value="rap")
ext_var = tk.StringVar(value="flac")
type_var = tk.StringVar(value="single")  # single or album

# File + Folder Selectors
def select_url_file():
    path = filedialog.askopenfilename(title="Select url.txt file", filetypes=[("Text files", "*.txt")])
    if path:
        url_path_var.set(path)

def select_output_folder():
    path = filedialog.askdirectory(title="Select download base folder")
    if path:
        output_path_var.set(path)

# Download Logic
def start_download():
    url_file = url_path_var.get()
    output_folder = output_path_var.get()
    genre = genre_var.get().strip()
    ext = ext_var.get().lower()
    content_type = type_var.get()

    if not url_file or not output_folder or not genre:
        messagebox.showerror("Missing input", "Please fill out all fields.")
        return

    def task():
        full_output_path = os.path.join(output_folder, ext, genre)

        if content_type == "single":
            ytdl.process_url_list(url_file, genre, ext, output_folder)
            album_name = os.path.splitext(os.path.basename(url_file))[0]
            pairDIR.organize_album_files(output_folder, ext, genre, f".{ext}")


        else:
            playList.process_url_list(url_file, genre, ext, output_folder)
            album_name = os.path.splitext(os.path.basename(url_file))[0]
            plPair.organize_album_into_folder(full_output_path, album_name, f".{ext}")

        messagebox.showinfo("Done", f"✅ All downloads and organization done in:\n{full_output_path}")

    threading.Thread(target=task, daemon=True).start()

# GUI Layout
tk.Label(root, text="1. Select url.txt file:").pack()
tk.Entry(root, textvariable=url_path_var, width=50).pack()
tk.Button(root, text="Browse URL File", command=select_url_file).pack(pady=5)

tk.Label(root, text="2. Select content type:").pack()
tk.OptionMenu(root, type_var, "single", "album").pack(pady=5)

tk.Label(root, text="3. Enter genre:").pack()
tk.Entry(root, textvariable=genre_var, width=30).pack(pady=5)

tk.Label(root, text="4. Select audio format:").pack()
tk.OptionMenu(root, ext_var, "flac", "m4a", "mp3").pack(pady=5)

tk.Label(root, text="5. Select output base folder:").pack()
tk.Entry(root, textvariable=output_path_var, width=50).pack()
tk.Button(root, text="Browse Output Folder", command=select_output_folder).pack(pady=5)

tk.Button(root, text="🚀 Start Download", command=start_download, bg="green", fg="white").pack(pady=20)

root.mainloop()
