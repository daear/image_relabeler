# Image Renamer  
A lightweight, scrollable GUI that lets you batch-review, rename, and delete images in a single folder. Janky but workable!

![Screenshot](screenshot.png)

---

## Features
- **Visual preview** – 150 × 150 thumbnails for every image  
- **Inline editing** – type a new name, hit Enter or click Rename  
- **Smart conflict guard** – warns if the new name already exists  
- **Quick actions**  
  - Remove from list (keeps file, hides row)  
  - Delete file permanently (no confirmation prompt)  
- **Auto-fit window** – width expands to fit content, height locked at 800 px  
- **Cross-platform mouse-wheel scrolling** (Windows, macOS, Linux)

---

## Supported Formats
```png```, ```jpg```, ```jpeg```, ```gif```, ```bmp```, ```webp```

---

## Requirements
- Python 3.7+  
- Pillow (```pip install pillow```)

---

## How to Run
```bash
git clone https://github.com/your-username/image-renamer.git
cd image-renamer
pip install pillow
python image_renamer.py
```
1. A folder-picker opens—choose the directory that contains your images.  
2. Edit filenames in the text boxes.  
3. Press Enter or the Rename button to apply the change and move to the next row.  
4. Use the ⬇ button to skip a file or the 🗑️ button to delete it outright.

---

## License
MIT – do whatever you want.

