import os
import re
import zipfile
from PIL import Image
import tempfile
import argparse
import shutil

# Set of valid image extensions to improve lookup speed
VALID_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg'}

def get_file_size(file_path):
    """Returns the file size in megabytes."""
    size_in_bytes = os.path.getsize(file_path)
    return size_in_bytes / (1024 * 1024)  # Convert bytes to megabytes

def compress_cbz(file_path, output_path=None, quality=80, max_height=1024):
    if output_path is None:
        output_path = file_path

    original_size = get_file_size(file_path)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract all files to a temp directory
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        compressed_path = os.path.join(temp_dir, "compressed.cbz")
        # Compress and optionally resize each image
        with zipfile.ZipFile(compressed_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_path = os.path.join(root, file)
                        with Image.open(img_path) as img:
                            if img.mode == 'P':
                                img = img.convert('RGB')
                            # Check if the image height is greater than the max height
                            if img.height > max_height:
                                aspect_ratio = img.width / img.height
                                new_width = int(aspect_ratio * max_height)
                                img = img.resize((new_width, max_height), Image.LANCZOS)
                        
                            # Save the compressed image back to the temporary directory
                            img_compressed_path = os.path.join(temp_dir, file)
                            img.save(img_compressed_path, "JPEG", quality=quality)
                            arcname = os.path.relpath(img_compressed_path, temp_dir)
                            zipf.write(img_compressed_path, arcname)

        compressed_size = get_file_size(compressed_path)
        size_saved = original_size - compressed_size

        # Move the compressed file to the desired location
        shutil.move(compressed_path, output_path)
    return size_saved

def clean_file_naming(filename, prefix, start_number):
    """Clean and rename the filename."""
    
    # Remove content inside parentheses
    cleaned_name = re.sub(r'\(.*?\)', '', filename)
    # Remove multiple consecutive spaces
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name)
    # Rename the file using the specified naming format
    base, extension = os.path.splitext(cleaned_name)
    cleaned_name = f"{prefix}{start_number:03}{extension}"
    return cleaned_name

def process_files(directory, prefix, start_number, quality, max_height):
    """Process and rename .cbz files in the given directory."""
    
    counter = start_number
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if filename.endswith('.cbz'):
            size_saved = compress_cbz(filepath, quality=quality, max_height=max_height)
            new_filename = clean_file_naming(filename, prefix, counter)
            new_file_path = os.path.join(directory, new_filename)
            if new_file_path != filepath:
                os.rename(filepath, new_file_path)
                counter += 1
            print(f"✅ Compressed {os.path.basename(filepath)} to {new_filename} | Size saved: {size_saved:.2f} MB")

def get_args():
    """Parse command line arguments and, if missing, prompt the user for input."""
    
    parser = argparse.ArgumentParser(description='Process and rename .cbz files.')
    parser.add_argument('--dir', default='./input/', help='Directory containing the .cbz files')
    parser.add_argument('--prefix', help='New prefix for renaming files')
    parser.add_argument('--start-number', type=int, help='Starting number for renaming files')
    parser.add_argument('--quality', type=int, help='Image compression quality (1-100)')
    parser.add_argument('--max-height', type=int, help='Maximum height for images')
    args = parser.parse_args()
    
    # If arguments are missing, prompt the user for input
    args.prefix = args.prefix or input("Enter the title of the series: ")
    args.start_number = args.start_number or int(input("Enter the starting number (default 1): ") or "1")
    args.quality = args.quality or int(input("Enter image compression quality (1-100, default 80): ") or "80")
    args.max_height = args.max_height or int(input("Enter maximum height for images (default 1024): ") or "1024")
    
    return args

def main():
    """Main function to start the process."""
    args = get_args()
    process_files(args.dir, args.prefix, args.start_number, args.quality, args.max_height)

if __name__ == "__main__":
    main()
