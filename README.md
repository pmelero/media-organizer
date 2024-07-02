
# Media File Organizer Script

This script organizes media files (images and videos) into directories based on the date the media was created. The script supports various image and video formats and uses EXIF data or creation date metadata to determine the correct date.

## Disclaimer

- This script is provided "as-is" and is used at your own risk. The author is not responsible for any damage, data loss, or any other issues that may arise from using this script.
- Ensure you have a backup of your files before using this script.
- Make sure the files you want to organize are stored in a specific folder.

## Features

- Supports `jpg`, `jpeg`, `png`, `heic`, `heif`, `dng`, `mp4`, `mov`, and `avi` file formats.
- Organizes files into directories structured as `/year/month`.
- Handles duplicate files by renaming them if they have different EXIF data.
- Logs operations including files moved, deleted, replaced, and renamed.

## Requirements

- Python 3.9+
- `pip` (Python package installer)
- Docker (optional, for running in a containerized environment)

## Installation

### Using Docker

1. Install Docker:
   - [Docker Installation Guide](https://docs.docker.com/get-docker/)

2. Clone this repository:

   ```sh
   git clone https://github.com/your-repository/media-file-organizer.git
   cd media-file-organizer
   ```

3. Build the Docker image:

   ```sh
   docker build -t media-organizer .
   ```

### Without Docker

1. Install dependencies:

   ```sh
   sudo apt-get update
   sudo apt-get install -y ffmpeg
   pip install -r requirements.txt
   ```

## Usage

### Using Docker

1. Run the Docker container with the source folder mounted:

   ```sh
   docker run --rm -v /path/to/your/source_folder:/app/source_folder media-organizer /app/source_folder
   ```

### Without Docker

1. Run the script directly:

   ```sh
   python media-organizer.py /path/to/your/source_folder
   ```

### Parameters

- `source_folder`: Path to the folder containing media files to be organized.

### Notes

- The destination folder will be created automatically as `source_folder/_output` in the same directory as the `source_folder`.
- The script will generate an `output_log.txt` in the destination folder, detailing the operations performed on the files.

## Example

### Example Command

```sh
python media-organizer.py /mnt/d/Fotos/Iphone
```
### Example Input Structure

```
/mnt/d/Fotos/Iphone/
├── 202301__/
│   ├── img001.jpg
│   └── video001.mp4
├── 202302__/
│   ├── img002.jpg
│   └── video002.mp4
├── 202403__/
│   ├── img003.jpg
│   └── video003.mp4
├── 202404__/
│   ├── img004.jpg
│   └── video004.mp4
```

### Example Output Structure

After running the script, the folder structure will look like this:

```
/mnt/d/Fotos/Iphone/_output/
├── 2023/
│   ├── 01/
│   │   ├── img001.jpg
│   │   ├── video001.mp4
│   └── 02/
│       ├── img002.jpg
│       └── video002.mp4
├── 2024/
│   ├── 03/
│   │   ├── img003.jpg
│   │   └── video003.mp4
│   └── 04/
│       ├── img004.jpg
│       └── video004.mp4
output_log.txt
```

## Troubleshooting

If you encounter an error like `No such file or directory: 'ffprobe'`, ensure `ffmpeg` is installed and accessible in your system's PATH. On a Linux system, you can install `ffmpeg` with:

```sh
sudo apt-get install -y ffmpeg
```

info: ffmpeg-next package, [follow this guide](https://github.com/zmwangx/rust-ffmpeg/wiki/Notes-on-building)

## WSL Instructions for Windows

To use the script in a Windows environment with WSL (Windows Subsystem for Linux):

1. Install WSL and a Linux distribution like Ubuntu from the Microsoft Store.
2. Follow the installation and usage instructions provided above for a Linux environment.

## License

This project is licensed under the MIT License.
