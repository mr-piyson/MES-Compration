# Image Compressor

A user-friendly GUI application for batch compressing images in nested directories. This tool recursively processes all images in a selected directory structure, compressing them to reduce file sizes while maintaining visual quality.

## Features

- **Intuitive GUI**: Clean, easy-to-use interface built with Tkinter
- **Batch Processing**: Processes multiple images across nested directories automatically
- **Adjustable Quality**: Compression quality slider (1-100) for fine-tuning
- **Real-time Progress**: Live progress bar and detailed logging
- **Format Support**: Handles JPG, JPEG, PNG, BMP, GIF, TIFF, and WEBP formats
- **Space Savings**: Shows compression statistics and space saved
- **In-place Compression**: Replaces original files with compressed versions
- **Stop/Resume**: Start and stop compression process at any time

## Directory Structure Support

The program works with nested directory structures like:
```
root_directory/
├─ folder1/
│  ├─ image1.jpg
│  ├─ image2.png
│  └─ image3.webp
├─ folder2/
│  ├─ subfolder/
│  │  └─ image4.jpg
│  └─ image5.png
└─ folder3/
   └─ image6.jpg
```

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

### Option 1: Run from Source

1. **Clone or download the project files**
   ```bash
   git clone <repository-url>
   cd image-compressor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python image_compressor.py
   ```

### Option 2: Use Pre-built Executable

1. Download the `ImageCompressor.exe` file from the releases
2. Double-click to run (no installation required)

## Building Executable

To create your own executable file:

### Prerequisites for Building
- Python 3.7+
- PyInstaller

### Build Steps

1. **Install build dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Build executable**
   ```bash
   pyinstaller --onefile --windowed --name="ImageCompressor" image_compressor.py
   ```

3. **Find your executable**
   - The executable will be created in the `dist/` folder
   - File name: `ImageCompressor.exe` (Windows) or `ImageCompressor` (Linux/Mac)

### Advanced Build Options

For a more customized build, you can use additional PyInstaller options:

```bash
# With icon (if you have an icon file)
pyinstaller --onefile --windowed --icon=icon.ico --name="ImageCompressor" image_compressor.py

# With additional data files
pyinstaller --onefile --windowed --add-data "README.md;." --name="ImageCompressor" image_compressor.py

# Console version (shows console window for debugging)
pyinstaller --onefile --console --name="ImageCompressor" image_compressor.py
```

### Build Script

For convenience, you can create a build script:

**Windows (build.bat):**
```batch
@echo off
echo Installing requirements...
pip install -r requirements.txt
echo Building executable...
pyinstaller --onefile --windowed --name="ImageCompressor" image_compressor.py
echo Build complete! Check the 'dist' folder.
pause
```

**Linux/Mac (build.sh):**
```bash
#!/bin/bash
echo "Installing requirements..."
pip install -r requirements.txt
echo "Building executable..."
pyinstaller --onefile --windowed --name="ImageCompressor" image_compressor.py
echo "Build complete! Check the 'dist' folder."
```

## Usage

1. **Launch the application**
   - Run `python image_compressor.py` or double-click the executable

2. **Select Directory**
   - Click "Browse" button
   - Choose the root directory containing your image folders

3. **Adjust Compression Quality**
   - Use the slider to set quality (1-100)
   - Higher values = better quality, larger files
   - Lower values = smaller files, reduced quality
   - Recommended: 80-90 for good balance

4. **Start Compression**
   - Click "Start Compression"
   - Monitor progress in the progress bar and log
   - View real-time statistics

5. **Monitor Progress**
   - Progress bar shows overall completion
   - Log shows detailed information for each file
   - Statistics display space saved

## Compression Quality Guide

| Quality | Use Case | File Size | Visual Quality |
|---------|----------|-----------|----------------|
| 90-100  | Professional/Print | Largest | Excellent |
| 80-89   | Web/General Use | Medium | Very Good |
| 70-79   | Web Optimization | Small | Good |
| 50-69   | Heavy Compression | Smaller | Fair |
| 1-49    | Maximum Compression | Smallest | Poor |

## Supported Image Formats

- **Input**: JPG, JPEG, PNG, BMP, GIF, TIFF, WEBP
- **Output**: Maintains original format (or converts to JPG for unsupported formats)

## Safety Features

- **Backup Recommendation**: Always backup your images before compression
- **In-place Processing**: Original files are replaced (cannot be undone)
- **Error Handling**: Continues processing even if individual files fail
- **Stop Function**: Can stop processing at any time

## Troubleshooting

### Common Issues

**"No module named 'PIL'"**
```bash
pip install Pillow
```

**"Permission denied" errors**
- Ensure you have write permissions to the image directories
- Close any programs that might be using the images

**Executable doesn't run**
- Make sure you built with `--windowed` flag for GUI applications
- Try building with `--console` to see error messages

**Images not being processed**
- Check that image files have supported extensions
- Verify directory path is correct
- Check file permissions

### Performance Tips

- Close other applications to free up memory for large batches
- For very large directories (1000+ images), consider processing in smaller batches
- SSD storage will significantly improve processing speed

## Technical Details

- **GUI Framework**: Tkinter (included with Python)
- **Image Processing**: Pillow (PIL)
- **Threading**: Multi-threaded to prevent GUI freezing
- **Supported Platforms**: Windows, macOS, Linux

## File Structure

```
image-compressor/
├── image_compressor.py    # Main application file
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── build.bat             # Windows build script (optional)
└── dist/                 # Generated executables (after build)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Feel free to modify and distribute.

## Changelog

### v1.0.0
- Initial release
- Basic GUI with compression functionality
- Progress tracking and logging
- Multi-format support
- Recursive directory processing

---

**⚠️ Important**: Always backup your images before using this tool. The compression process replaces original files and cannot be undone.