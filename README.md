# Manga CBZ Processor

Python tool optimized for manga `.cbz` files. It efficiently compresses, resizes, and renames files, ensuring optimal storage and clarity while preserving the essence of your favorite manga.

## Features

1. **Compression**: The script compresses the `.cbz` files to reduce their file size.
2. **Resizing**: Images inside the `.cbz` files are resized if their height is greater than a set limit (e.g., 1024 pixels) while preserving their aspect ratio.
3. **Renaming**: The script renames files to remove any content inside parentheses from the filename.

## Requirements

- Python 3.x
- Pillow library: `pip install Pillow`

## Usage

1. Clone the repository:

   ```bash
   git clone [your-repo-link]
   cd [repository-name]

   ```

1. Ensure you have the Pillow library installed:

   ```bash
   pip install Pillow
   ```

1. Put all your `.cbz` files in the `input` folder.

1. Run the script:

   ```bash
   python cbz_processor.py
   ```
