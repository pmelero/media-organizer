import argparse
from datetime import datetime
import io
import os
import shutil

from PIL import Image
from PIL.ExifTags import TAGS
import exifread
import ffmpeg
import pyheif
from tqdm import tqdm

def ios_extract_year_month_folder(source_folder):
    # List all directories inside the given source_folder
    folders = [name for name in os.listdir(source_folder) if os.path.isdir(os.path.join(source_folder, name))]
    year_month = []

    for folder in folders:
        # Assume folders have the format YYYYMM__
        if len(folder) >= 6:
            year = folder[:4]
            month = folder[4:6]
            if year.isdigit() and month.isdigit():
                year_month.append((folder, year, month))

    return year_month

def ios_move_files_to_destination(source_folder):
    destination_folder = source_folder + '/_output'    
    year_month_folders = ios_extract_year_month_folder(source_folder)

    for folder, year, month in year_month_folders:
        # Create destination path
        dest_path = os.path.join(destination_folder, year, month)
        os.makedirs(dest_path, exist_ok=True)
        
        # Source path for the current folder
        source_path = os.path.join(source_folder, folder)
        
        # List all files in the current folder
        files = [f for f in os.listdir(source_path) if os.path.isfile(os.path.join(source_path, f))]
        
        for file in files:
            # Construct full file paths
            src_file = os.path.join(source_path, file)
            dst_file = os.path.join(dest_path, file)
            
            # Move file to the destination
            shutil.move(src_file, dst_file)

def get_image_date_taken(path):
    try:
        if path.lower().endswith(('heic', 'heif')):
            heif_file = pyheif.read(path)
            for metadata in heif_file.metadata or []:
                if metadata['type'] == 'Exif':
                    tags = exifread.process_file(io.BytesIO(metadata['data'][6:]))
                    if 'EXIF DateTimeOriginal' in tags:
                        date_str = str(tags['EXIF DateTimeOriginal'])
                        return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        elif path.lower().endswith('dng'):
            with open(path, 'rb') as f:
                tags = exifread.process_file(f)
                if 'EXIF DateTimeOriginal' in tags:
                    date_str = str(tags['EXIF DateTimeOriginal'])
                    return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        else:
            image = Image.open(path)
            info = image._getexif()
            if info:
                exif_data = {TAGS.get(tag, tag): value for tag, value in info.items()}
                if 'DateTimeOriginal' in exif_data:
                    return datetime.strptime(exif_data['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
                return exif_data
    except Exception as e:
        print(f"Error reading EXIF data from {path}: {e}")
    return None

def get_video_creation_date(path):
    try:
        probe = ffmpeg.probe(path)
        if 'format' in probe and 'tags' in probe['format']:
            tags = probe['format']['tags']
            if 'creation_time' in tags:
                return datetime.strptime(tags['creation_time'], '%Y-%m-%dT%H:%M:%S.%fZ')
    except Exception as e:
        print(f"Error reading video metadata from {path}: {e}")
    return None

def get_date_taken(path, file):
    if os.path.exists(path):
        if file.lower().endswith(('mp4', 'mov', 'avi')):
            date_taken = get_video_creation_date(path)
        else:
            exif_data = get_image_date_taken(path)
            if isinstance(exif_data, datetime):
                date_taken = exif_data
            else:
                date_taken = None
    return date_taken

def organize_files_by_date(source_folder):
    destination_folder = source_folder + '/_output'
    ensure_folder_exists(destination_folder)
    
    # Get the list of files to process
    files_to_process = get_files_to_process(source_folder)

    total_files = len(files_to_process)
    files_moved = 0
    files_deleted = 0
    files_replaced = 0
    files_renamed = 0
    files_not_moved = 0

    overwritten_files = []
    deleted_files = []
    renamed_files = []

    # Process files with a progress bar
    for root, file in tqdm(files_to_process, desc="Processing files", unit="file"):
        file_path = os.path.join(root, file)
        
        # Try to get the date the photo or video was take                
        date_taken = get_date_taken(file_path, file)
        
        if date_taken:
            year = date_taken.strftime('%Y')
            month = date_taken.strftime('%m')
            dest_dir = os.path.join(destination_folder, year, month)
                
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
                
            dest_path = os.path.join(dest_dir, file)            
            
            if os.path.exists(dest_path):         
                dest_date_taken = get_date_taken(dest_path, file) 
                if date_taken and date_taken != dest_date_taken:
                    new_file_name = f"{os.path.splitext(file)[0]}_1{os.path.splitext(file)[1]}"
                    dest_path = os.path.join(dest_dir, new_file_name)
                    shutil.move(file_path, dest_path)
                    files_renamed += 1
                    renamed_files.append(f"{file_path} -> {dest_path}")
                elif os.path.getsize(file_path) > os.path.getsize(dest_path):
                    shutil.move(file_path, dest_path)
                    files_replaced += 1
                    overwritten_files.append(f"{file_path} -> {dest_path}")
                else:
                    os.remove(file_path)
                    files_deleted += 1
                    deleted_files.append(f"[X] {file_path} ({dest_path})")
            else:
                shutil.move(file_path, dest_path)
                files_moved += 1
        else:
            files_not_moved += 1

    # Show process summary
    print(f"\nTotal files processed: [{total_files}/{total_files}]")
    print(f"Total files moved: [{files_moved}/{total_files}]")
    print(f"Total files not moved: [{files_not_moved}/{total_files}]")
    print(f"Total files deleted: [{files_deleted}/{total_files}]")
    print(f"Total files replaced: [{files_replaced}/{total_files}]")
    print(f"Total files renamed: [{files_renamed}/{total_files}]")
    
    # Write log file    
    dateTime = datetime.now()
    filename = dateTime.strftime("%Y%m%d_%H%M%S")
    
    with open(os.path.join(destination_folder, f'{filename}_log.txt'), 'w') as log_file:
        log_file.write(f"Total files processed: {total_files}\n")
        log_file.write(f"Total files moved: [{files_moved}/{total_files}]\n")
        log_file.write(f"Total files not moved: [{files_not_moved}/{total_files}]\n")
        log_file.write(f"Total files deleted: [{files_deleted}/{total_files}]\n")
        log_file.write(f"Total files replaced: [{files_replaced}/{total_files}]\n")
        log_file.write(f"Total files renamed: [{files_renamed}/{total_files}]\n")
        
        if overwritten_files:
            log_file.write("\nOverwritten files:\n")
            for file in overwritten_files:
                log_file.write(f"{file}\n")
        if renamed_files:
            log_file.write("\nRenamed files:\n")
            for file in renamed_files:
                log_file.write(f"{file}\n")     
        if deleted_files:
            log_file.write("\nDeleted files:\n")
            for file in deleted_files:
                log_file.write(f"{file}\n")

def get_files_to_process(source_folder):
    files_to_process = []
    for root, _, files in os.walk(source_folder):
        if '_output' in root:
            continue
        for file in files:
            if file.lower().endswith(('jpg', 'jpeg', 'png', 'heic', 'heif', 'dng', 'mp4', 'mov', 'avi')):
                files_to_process.append((root, file))
    return files_to_process

def ensure_folder_exists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organize media files by date.")
    parser.add_argument("source_folder", help="Path to the source folder containing media files.")
    args = parser.parse_args()

    organize_files_by_date(args.source_folder)
    ios_move_files_to_destination(args.source_folder)