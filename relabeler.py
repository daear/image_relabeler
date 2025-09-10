import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

THUMB_SIZE = (150, 150)  # thumbnails 150x150
MIN_WIDTH = 960          # 20% narrower default than 1200, expands to fit content
FIXED_HEIGHT = 800


class ImageRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Renamer")
        self.root.geometry(f"{MIN_WIDTH}x{FIXED_HEIGHT}")  # narrower default

        # Choose directory at startup
        self.directory = filedialog.askdirectory(title="Select Image Directory")
        if not self.directory:
            root.destroy()
            return

        # Canvas + scrollbar for scrolling
        self.canvas = tk.Canvas(root, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.container = tk.Frame(self.canvas)  # holds the grid
        self.container.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.container, anchor="nw")

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind mouse wheel for all platforms
        self._bind_mousewheel()

        # Data/state
        self.items = []          # list of {"path": str, "name": str, "ext": str}
        self.entry_widgets = []  # parallel list of Entry widgets
        self.image_refs = []     # keep thumbnails alive

        self.load_items()
        self.build_ui()
        self._resize_to_content()

    # ---------- Data loading ----------
    def load_items(self):
        self.items.clear()
        for filename in sorted(os.listdir(self.directory)):
            path = os.path.join(self.directory, filename)
            if not os.path.isfile(path):
                continue
            if not filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")):
                continue
            name, ext = os.path.splitext(filename)
            self.items.append({"path": path, "name": name, "ext": ext})

    # ---------- UI building ----------
    def build_ui(self):
        # Clear UI
        for w in self.container.winfo_children():
            w.destroy()
        self.entry_widgets.clear()
        self.image_refs.clear()

        for i, item in enumerate(self.items):
            self._add_row(i, item)

        self.container.update_idletasks()
        self._resize_to_content()

    def _add_row(self, idx, item):
        path, name, ext = item["path"], item["name"], item["ext"]
        filename = name + ext

        # Thumbnail
        try:
            img = Image.open(path)
            img.thumbnail(THUMB_SIZE)
            photo = ImageTk.PhotoImage(img)
            self.image_refs.append(photo)  # prevent GC
            tk.Label(self.container, image=photo).grid(row=idx, column=0, padx=5, pady=5, sticky="w")
        except Exception:
            # If thumbnail fails, put a placeholder label
            tk.Label(self.container, text="[thumb]", width=18, anchor="w").grid(row=idx, column=0, padx=5, pady=5, sticky="w")

        # Current filename
        tk.Label(self.container, text=filename, width=60, anchor="w").grid(row=idx, column=1, padx=5, sticky="w")

        # Entry (no extension)
        e = tk.Entry(self.container, width=40)
        e.grid(row=idx, column=2, padx=5, sticky="w")
        e.insert(0, name)
        e.bind("<FocusIn>", lambda ev, ent=e: self._select_all(ent))
        e.bind("<Control-a>", lambda ev, ent=e: self._select_all(ent, consume=True))
        e.bind("<Return>", lambda ev, i=idx: self.rename_and_remove(i))
        self.entry_widgets.append(e)

        # Rename button
        tk.Button(self.container, text="Rename", command=lambda i=idx: self.rename_and_remove(i)).grid(row=idx, column=3, padx=5)

        # ⬇ remove-from-list button
        tk.Button(self.container, text="⬇", command=lambda i=idx: self.remove_row(i)).grid(row=idx, column=4, padx=5)

        # ☠ delete file button (no prompt)
        tk.Button(self.container, text="🗑️", command=lambda i=idx: self.delete_file(i)).grid(row=idx, column=5, padx=5)

    # ---------- Actions ----------
    def rename_and_remove(self, index):
        if index < 0 or index >= len(self.items):
            return
        item = self.items[index]
        entry = self.entry_widgets[index]

        new_name = entry.get().strip()
        if not new_name:
            messagebox.showerror("Error", "Filename cannot be empty.")
            return

        old_path = item["path"]
        new_filename = new_name + item["ext"]
        new_path = os.path.join(self.directory, new_filename)

        if os.path.exists(new_path):
            messagebox.showerror("Error", f"File '{new_filename}' already exists.")
            return

        try:
            os.rename(old_path, new_path)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        # Remove from list and rebuild UI
        self.items.pop(index)
        self.build_ui()
        self.focus_top_entry()

    def remove_row(self, index):
        if 0 <= index < len(self.items):
            self.items.pop(index)
            self.build_ui()

    def delete_file(self, index):
        if 0 <= index < len(self.items):
            path = self.items[index]["path"]
            try:
                os.remove(path)
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return
            self.items.pop(index)
            self.build_ui()

    # ---------- Helpers ----------
    def focus_top_entry(self):
        if self.entry_widgets:
            self.canvas.yview_moveto(0.0)
            top = self.entry_widgets[0]
            top.focus_set()
            self._select_all(top)

    def _select_all(self, entry_widget, consume=False):
        entry_widget.select_range(0, "end")
        entry_widget.icursor("end")
        return "break" if consume else None

    def _resize_to_content(self):
        self.root.update_idletasks()
        content_w = self.container.winfo_reqwidth() + 40  # padding for scrollbar
        width = max(MIN_WIDTH, content_w)
        self.root.geometry(f"{width}x{FIXED_HEIGHT}")

    # Cross-platform mouse wheel binding
    def _bind_mousewheel(self):
        # Windows & macOS
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # Linux (X11)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        try:
            if event.num == 4:       # Linux scroll up
                self.canvas.yview_scroll(-3, "units")
            elif event.num == 5:     # Linux scroll down
                self.canvas.yview_scroll(3, "units")
            else:
                # Windows/macOS: event.delta is ±120 multiples
                delta = -1 if event.delta > 0 else 1
                self.canvas.yview_scroll(delta * 3, "units")
        except Exception:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageRenamerApp(root)
    root.mainloop()
