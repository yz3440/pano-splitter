# Pano Splitter GUI v0.0.1 - Complete Panoramic Image Converter

🎉 **First Release**: A comprehensive graphical user interface for converting 360-degree panoramic images into perspective views with parallel processing support.

## 🆕 What's New

This release introduces a complete GUI application that makes panoramic image processing accessible to everyone - no command line experience required!

### ✨ Key Features

#### 🖼️ **Single Image Processing**

- **Visual Interface**: Browse and preview panoramic images before processing
- **Real-time Preview**: See your selected image in the interface
- **Customizable Parameters**:
  - Field of View: 30-180 degrees
  - Output dimensions: 100x100 to 4000x4000 pixels
  - Camera angles: Full 360° coverage with pitch (1-179°) and yaw (0-360°)
- **Multiple Formats**: Export as JPG, PNG, or JPEG
- **Parallel Processing**: Multi-threaded generation for faster results

#### 📁 **Batch Processing**

- **Directory Processing**: Convert entire folders of panoramic images
- **Progress Tracking**: Visual progress bar and detailed logging
- **Smart Format Detection**: Auto-detect input formats or specify output format
- **Performance Tuning**: Configurable worker threads for optimal system utilization
- **Comprehensive Logging**: Track processing status for each image

#### ⚡ **Performance Benchmark**

- **Speed Testing**: Compare sequential vs parallel processing performance
- **Detailed Metrics**: Get precise timing and throughput measurements
- **Configurable Tests**: Adjust perspectives, iterations, and worker threads
- **Visual Results**: Clear performance comparison with speedup analysis

#### ⚙️ **Advanced Settings**

- **Default Configurations**: Set up your preferred angles and parameters
- **System Optimization**: Configure threading for your hardware
- **Process Control**: Cancel operations at any time
- **Settings Persistence**: Save your preferences across sessions

## 🚀 Quick Start

### Option 1: Download & Run (Recommended)

1. Download the appropriate executable for your system from the assets below
2. Double-click to run - no installation required!
3. Start processing your panoramic images immediately

### Option 2: Build from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/pano-splitter.git
cd pano-splitter

# Install dependencies (requires uv)
uv sync
uv add pyinstaller

# Build executable
uv run python build_gui.py
```

## 📦 Downloads

| Platform                    | File                        | Size  | SHA256   |
| --------------------------- | --------------------------- | ----- | -------- |
| macOS (Intel/Apple Silicon) | `PanoSplitter-macos.zip`    | ~60MB | `[hash]` |
| Windows (64-bit)            | `PanoSplitter-windows.exe`  | ~65MB | `[hash]` |
| Linux (64-bit)              | `PanoSplitter-linux.tar.gz` | ~58MB | `[hash]` |

## 💻 System Requirements

### Minimum Requirements

- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+ equivalent)
- **RAM**: 4GB (8GB recommended for large images)
- **Storage**: 200MB free space + space for output images
- **CPU**: Multi-core processor recommended for optimal performance

### Recommended Specifications

- **RAM**: 16GB+ for processing large panoramic images (>8K resolution)
- **Storage**: SSD for faster I/O performance
- **CPU**: 8+ cores for maximum parallel processing benefit

## 🎯 Use Cases

### Perfect For:

- **Real Estate**: Create multiple perspective views from 360° property photos
- **Virtual Tours**: Generate individual views from panoramic captures
- **Architecture**: Extract specific angles from architectural panoramas
- **Photography**: Convert spherical images to traditional perspective views
- **VR Content**: Prepare panoramic content for different viewing formats

### Sample Workflows:

1. **Real Estate Photography**: Process entire folders of property panoramas into standard views
2. **Architecture Documentation**: Extract specific angles (front, sides, interior views) from 360° captures
3. **Performance Testing**: Benchmark your system's image processing capabilities

## 🔧 Technical Details

### Built With:

- **Python 3.8+**: Core application logic
- **OpenCV**: High-performance image processing
- **NumPy**: Efficient numerical computations
- **Pillow**: Image handling and format support
- **Tkinter**: Cross-platform GUI framework
- **PyInstaller**: Executable generation

### Processing Engine:

- **Equirectangular Input**: Standard 360° panoramic format
- **Rectilinear Output**: Traditional perspective projections
- **Parallel Processing**: ThreadPoolExecutor for optimal performance
- **Memory Efficient**: Optimized for large image processing

### Coordinate System:

- **Pitch (Vertical)**: 1-179° (60°=up, 90°=horizon, 120°=down)
- **Yaw (Horizontal)**: 0-360° (0°=front, 90°=right, 180°=back, 270°=left)
- **FOV**: 30-180° field of view control

## 📋 What's Included

### Executables:

- `PanoSplitter` - Main GUI application
- Complete dependency bundling (no separate installation needed)

### Documentation:

- `README_GUI.md` - Comprehensive user guide
- Installation and usage instructions
- Troubleshooting guide

### Build Tools:

- `build_gui.py` - Executable build script
- `install_windows.bat` / `install_unix.sh` - Platform-specific installers
- `requirements_gui.txt` - Python dependencies

## 🔄 CLI Compatibility

This GUI version maintains full compatibility with existing CLI tools:

- `pano_splitter.py` - Batch processing via command line
- `single_pano_splitter.py` - Single image processing via command line
- Same parameters, same output quality, same performance

## 🐛 Known Issues

- **Large Images**: Processing >8K panoramic images may require significant RAM
- **macOS Security**: On macOS, you may need to right-click → "Open" for first run
- **Windows Defender**: Antivirus may flag the executable (false positive)

## 🔮 Future Plans

- **GPU Acceleration**: CUDA/OpenCL support for faster processing
- **Additional Formats**: Support for more input/output formats
- **Batch Templates**: Pre-configured angle sets for common use cases
- **Advanced Preview**: 3D preview of generated perspectives

## 🙏 Acknowledgments

Built on the foundation of the original pano-splitter CLI tools, enhanced with:

- Modern GUI framework
- Parallel processing optimizations
- User-friendly interface design
- Comprehensive error handling

## 📝 Changelog

### v0.0.1 (Initial Release)

- ✨ Complete GUI application with tabbed interface
- 🖼️ Single image processing with preview
- 📁 Batch processing with progress tracking
- ⚡ Performance benchmarking tools
- ⚙️ Advanced settings and configuration
- 🔧 Cross-platform executable generation
- 📚 Comprehensive documentation
- 🛠️ uv package manager integration

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines and feel free to:

- Report bugs or issues
- Suggest new features
- Submit pull requests
- Improve documentation

## 📄 License

This project is licensed under the same terms as the parent pano-splitter project.

---

**Download now and start converting your panoramic images with ease!** 🚀
