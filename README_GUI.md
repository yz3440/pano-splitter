# Pano Splitter GUI - Panoramic Image Converter

A comprehensive graphical user interface for converting 360-degree panoramic images into perspective views with parallel processing support.

## Features

### 🖼️ Single Image Processing

- Process individual panoramic images
- Real-time image preview
- Customizable camera angles (pitch and yaw)
- Adjustable field of view and output dimensions
- Multiple output formats (JPG, PNG, JPEG)
- Parallel processing for faster generation

### 📁 Batch Processing

- Process multiple images simultaneously
- Progress tracking with visual progress bar
- Auto-detect image formats or specify output format
- Configurable worker threads for optimal performance
- Comprehensive logging of processing status

### ⚡ Performance Benchmark

- Compare sequential vs parallel processing performance
- Configurable test parameters
- Detailed performance metrics and speedup analysis
- Visual results display

### ⚙️ Advanced Settings

- Customizable default angles for all processing modes
- Multi-threading configuration
- Real-time processing logs
- Cancel operations at any time

## Installation

### Option 1: Use Pre-built Executable (Recommended)

1. Download the latest executable from the releases page
2. Run `PanoSplitter.exe` (Windows) or `PanoSplitter` (Linux/macOS)
3. No additional installation required!

### Option 2: Build from Source

#### Prerequisites

- Python 3.8 or higher
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager

#### Quick Install (Windows)

```bash
# Clone or download the repository
# Navigate to the project directory
install_windows.bat
```

#### Quick Install (Linux/macOS)

```bash
# Clone or download the repository
# Navigate to the project directory
chmod +x install_unix.sh
./install_unix.sh
```

#### Manual Install

```bash
# Install dependencies
uv sync

# Add PyInstaller
uv add pyinstaller

# Build executable
uv run python build_gui.py
```

## Usage

### Starting the Application

- **Executable**: Double-click the `PanoSplitter` executable
- **From Source**: Run `uv run python pano_splitter_gui.py`

### Single Image Processing

1. Go to the **Single Image** tab
2. Click **Browse** to select your panoramic image
3. Set output directory and parameters:
   - **Field of View**: 30-180 degrees
   - **Output Size**: Width and height in pixels
   - **Format**: JPG, PNG, or JPEG
   - **Angles**: Comma-separated pitch and yaw angles
4. Click **Process Image**
5. Monitor progress in the log panel

### Batch Processing

1. Go to the **Batch Processing** tab
2. Select input directory containing panoramic images
3. Set output directory and processing parameters
4. Configure worker threads for optimal performance
5. Click **Process All Images**
6. Track progress with the progress bar and logs

### Performance Benchmark

1. Go to the **Benchmark** tab
2. Select a test panoramic image
3. Configure benchmark parameters:
   - **Perspectives**: Number of views to generate
   - **Iterations**: Number of test runs
   - **Workers**: Parallel processing threads
4. Click **Run Benchmark**
5. View detailed performance results

### Settings Configuration

1. Go to the **Settings** tab
2. Set default pitch and yaw angles
3. Click **Apply to All Tabs** to use across all processing modes

## Camera Angle System

### Pitch Angles (Vertical)

- **Range**: 1-179 degrees
- **60°**: Looking upward
- **90°**: Looking straight ahead (horizon)
- **120°**: Looking downward

### Yaw Angles (Horizontal)

- **Range**: 0-360 degrees
- **0°**: Front view
- **90°**: Right view
- **180°**: Back view
- **270°**: Left view

### Common Angle Presets

- **360° Coverage**: `pitch=60,90,120` `yaw=0,60,120,180,240,300`
- **Horizon Views**: `pitch=90` `yaw=0,90,180,270`
- **Upward Views**: `pitch=30,60` `yaw=0,120,240`

## Output Files

Generated images are named using the pattern:

```
{image_name}_pitch{pitch}_yaw{yaw}_fov{fov}.{format}
```

Example: `panorama_pitch90_yaw0_fov100.jpg`

## Performance Tips

### Optimal Worker Configuration

- **CPU-bound**: Set workers = CPU cores
- **Memory-limited**: Reduce workers to prevent RAM exhaustion
- **Large images**: Use fewer workers per image, more image workers for batch

### Memory Management

- Large panoramic images (>8K) may require significant RAM
- Monitor system resources during processing
- Consider processing in smaller batches for very large datasets

### Processing Speed

- SSD storage significantly improves I/O performance
- Parallel processing scales well up to CPU core count
- GPU acceleration not currently supported

## Supported Formats

### Input Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- Case-insensitive extensions

### Output Formats

- JPEG: Smaller file size, faster processing
- PNG: Lossless quality, larger files
- Auto: Maintains original format

## Troubleshooting

### Common Issues

**"No supported image files found"**

- Ensure input directory contains .jpg, .jpeg, or .png files
- Check file permissions

**"Error loading preview"**

- Verify image file is not corrupted
- Ensure sufficient system memory

**"Processing failed"**

- Check available disk space in output directory
- Verify write permissions to output directory
- Reduce worker count if experiencing memory issues

**Application won't start**

- Ensure all dependencies are installed
- Check Python version (3.8+ required)
- Try running from command line to see error messages

### Performance Issues

**Slow processing**

- Reduce image resolution or worker count
- Close other memory-intensive applications
- Use SSD storage for input/output

**High memory usage**

- Process images in smaller batches
- Reduce number of simultaneous workers
- Consider using lower resolution outputs for testing

## Technical Details

### Dependencies

- **OpenCV**: Image processing and I/O
- **NumPy**: Numerical computations
- **Pillow**: Image handling and preview
- **Tkinter**: GUI framework (included with Python)

### Architecture

- Multi-threaded processing with ThreadPoolExecutor
- Queue-based logging system for thread-safe GUI updates
- Modular design with separation of GUI and processing logic

### Coordinate System

- Uses equirectangular projection input
- Generates rectilinear perspective outputs
- Coordinate conversion matches original CLI tools

## Building Executables

The build system uses `uv` and creates self-contained executables with all dependencies included:

```bash
# Build for current platform
uv run python build_gui.py

# Output location
dist/PanoSplitter(.exe)
```

### Build Configuration

- **Single file**: All dependencies in one executable
- **Windowed**: No console window (GUI only)
- **Cross-platform**: Build on target OS
- **Size**: Typically 50-100MB depending on platform

## Development

### Running from Source

```bash
# Install dependencies
uv sync

# Run the GUI
uv run python pano_splitter_gui.py

# Run CLI tools
uv run python pano_splitter.py --help
uv run python single_pano_splitter.py --help
```

### Adding Dependencies

```bash
# Add a new dependency
uv add package-name

# Update dependencies
uv sync
```

## License

This project uses the same license as the parent pano-splitter project.

## Support

For issues, feature requests, or questions:

1. Check this README for common solutions
2. Review the application logs for error details
3. Create an issue in the project repository

## Version History

### v1.0.0

- Initial GUI release
- Single image processing
- Batch processing
- Performance benchmarking
- Cross-platform executable support
- uv package manager integration
