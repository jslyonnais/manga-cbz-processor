import os
import re
import zipfile
from PIL import Image
import tempfile
import argparse

def get_file_size(file_path):
    """Returns the file size in megabytes."""
    size_in_bytes = os.path.getsize(file_path)
    return size_in_bytes / (1024 * 1024)  # Convert bytes to megabytes

def compress_cbz(file_path, output_path=None, quality=80, max_height=1024):
    if output_path is None:
        output_path = file_path

    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract all files to a temp directory
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Compress and optionally resize each image
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(root, file)
                    with Image.open(img_path) as img:
                        # Check if the image height is greater than the max height
                        if img.height > max_height:
                            aspect_ratio = img.width / img.height
                            new_width = int(aspect_ratio * max_height)
                            img = img.resize((new_width, max_height), Image.ANTIALIAS)
                        
                        img.save(img_path, "JPEG", quality=quality)

        # Create a new CBZ with the compressed (and optionally resized) images
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    img_path = os.path.join(root, file)
                    arcname = os.path.relpath(img_path, temp_dir)
                    zipf.write(img_path, arcname)

    # Calculate file size saved
    original_size = get_file_size(file_path)
    compressed_size = get_file_size(output_path)
    size_saved = original_size - compressed_size

    # Determine the new filename after renaming
    new_filename = clean_file_naming(os.path.basename(file_path), args.prefix, args.start_number)

    # Print the combined result with a green checkmark
    print(f"✅ Compressed {os.path.basename(file_path)} to {new_filename} | Size saved: {size_saved:.2f} MB")

def clean_file_naming(filename, prefix, start_number):
    # Remove content in parentheses
    cleaned_name = re.sub(r'\(.*?\)', '', filename)
    
    # Remove multiple consecutive spaces
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name)
    
    # Rename the file using the new naming format
    base, extension = os.path.splitext(cleaned_name)
    cleaned_name = f"{prefix}{start_number:03}{extension}"
    
    return cleaned_name

def process_files(directory, prefix, start_number, quality, max_height):
    counter = start_number
    
    # Iterate over each file in the directory
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if filename.endswith('.cbz'):
            # Compress the .cbz file
            compress_cbz(filepath, quality=quality, max_height=max_height)
            
            # Rename the file after removing content inside parentheses
            new_filename = clean_file_naming(filename, prefix, counter)
            new_file_path = os.path.join(directory, new_filename)
            
            if new_file_path != filepath:
                os.rename(filepath, new_file_path)
                counter += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process and rename .cbz files.')
    parser.add_argument('--dir', default='./input/', help='Directory containing the .cbz files', required=False)
    parser.add_argument('--prefix', default=None, help='New prefix for renaming files', required=False)
    parser.add_argument('--start-number', type=int, default=None, help='Starting number for renaming files', required=False)
    parser.add_argument('--quality', type=int, default=None, help='Image compression quality (1-100)', required=False)
    parser.add_argument('--max-height', type=int, default=None, help='Maximum height for images', required=False)
    
    args = parser.parse_args()
    
    # If args are not provided, prompt user for input
    if args.prefix is None:
        args.prefix = input("Enter the title of the series: ")

    if args.start_number is None:
        args.start_number = int(input("Enter the starting number (default 1): ") or "1")

    if args.quality is None:
        args.quality = int(input("Enter image compression quality (1-100, default 80): ") or "80")
    
    if args.max_height is None:
        args.max_height = int(input("Enter maximum height for images (default 1024): ") or "1024")
    
    process_files(args.dir, args.prefix, args.start_number, args.quality, args.max_height)
