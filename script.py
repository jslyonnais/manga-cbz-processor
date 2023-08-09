import os
import re
import zipfile
from PIL import Image
import tempfile

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

    print(f"Compressed {file_path}")

def clean_file_naming(filename):
    # Remove content in parentheses
    cleaned_name = re.sub(r'\(.*?\)', '', filename)
    
    # Remove multiple consecutive spaces
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name)
    
    # Remove spaces before the file extension
    base, extension = os.path.splitext(cleaned_name)
    cleaned_name = base.rstrip() + extension

    return cleaned_name

def process_files(directory):
    # Iterate over each file in the directory
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if filename.endswith('.cbz'):
            # Compress the .cbz file
            compress_cbz(filepath)
            
            # Rename the file after removing content inside parentheses
            new_filename = clean_file_naming(filename)
            new_file_path = os.path.join(directory, new_filename)
            
            if new_file_path != filepath:
                os.rename(filepath, new_file_path)
                print(f'Renamed {filename} to {new_filename}')

# Specify the directory containing the files to process
directory_path = "./files/"
process_files(directory_path)