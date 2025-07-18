import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import imagehash

HASH_SIZE = 8
SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')


class DuplicateFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate Image Finder")
        self.root.geometry("800x600")
        self.folder_path = ""
        self.hashes = {}
        self.duplicates = []

        self.select_btn = tk.Button(root, text="📁 Select Folder", command=self.select_folder)
        self.select_btn.pack(pady=10)

        self.result_label = tk.Label(root, text="")
        self.result_label.pack()

        # Canvas + Scrollbar Container
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="#2a2a2a")
        self.scrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.move_btn = tk.Button(root, text="🗃 Move Duplicates", command=self.move_duplicates, state=tk.DISABLED)
        self.move_btn.pack(pady=10)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return

        self.folder_path = folder
        self.hashes.clear()
        self.duplicates.clear()

        self.scan_folder()
        self.show_results()

    def scan_folder(self):
        for file in os.listdir(self.folder_path):
            if file.lower().endswith(SUPPORTED_EXTENSIONS):
                filepath = os.path.join(self.folder_path, file)
                try:
                    with Image.open(filepath) as img:
                        img_hash = imagehash.phash(img, hash_size=HASH_SIZE)
                        if img_hash in self.hashes:
                            self.duplicates.append(filepath)
                        else:
                            self.hashes[img_hash] = filepath
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")

    def show_results(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if self.duplicates:
            self.result_label.config(text=f"Found {len(self.duplicates)} duplicates:")
            self.move_btn.config(state=tk.NORMAL)
            self.display_images(self.duplicates)
        else:
            self.result_label.config(text="✅ No duplicates found.")
            self.move_btn.config(state=tk.DISABLED)

    def display_images(self, filepaths):
        self.canvas.images = []  # prevent garbage collection
        for path in filepaths:
            try:
                frame = tk.Frame(self.scrollable_frame, bg="#2a2a2a", pady=5)
                frame.pack(fill="x", padx=10)

                img = Image.open(path)
                img.thumbnail((100, 100))
                tk_img = ImageTk.PhotoImage(img)

                img_label = tk.Label(frame, image=tk_img, bg="#2a2a2a")
                img_label.pack(side="left", padx=10)
                text_label = tk.Label(frame, text=os.path.basename(path), fg="white", bg="#2a2a2a", font=("Arial", 11))
                text_label.pack(side="left", padx=10)

                self.canvas.images.append(tk_img)
            except Exception as e:
                print(f"Failed to show image {path}: {e}")

    def move_duplicates(self):
        dup_dir = os.path.join(self.folder_path, "duplicates")
        os.makedirs(dup_dir, exist_ok=True)
        for file in self.duplicates:
            shutil.move(file, os.path.join(dup_dir, os.path.basename(file)))
        messagebox.showinfo("Done", f"Moved {len(self.duplicates)} duplicate files to 'duplicates' folder.")
        self.select_folder()  # refresh


if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateFinderApp(root)
    root.mainloop()
