# Pano Splitter GUI

Graphical interface for converting panoramic images to perspective views.

## Features

- **Single Image Processing** - Process individual panoramic images with preview
- **Batch Processing** - Process multiple images simultaneously with progress tracking
- **Performance Benchmark** - Compare sequential vs parallel processing
- **Real-time Logs** - Monitor processing status
- **Configurable Settings** - Customize angles, output formats, and threading

## Installation

### Option 1: Pre-built Executable (Recommended)

1. Download `PanoSplitter-macos.zip` from releases
2. Extract and run `PanoSplitter`
3. No additional installation needed

### Option 2: Build from Source

```bash
# Install dependencies
uv sync

# Build executable
uv run python build_gui.py
```

## Usage

### Single Image Processing

1. **Single Image** tab → **Browse** to select panoramic image
2. Set output directory and parameters (FOV, dimensions, angles)
3. Click **Process Image**

### Batch Processing

1. **Batch Processing** tab → Select input/output directories
2. Configure processing parameters
3. Click **Process All Images**

### Performance Benchmark

1. **Benchmark** tab → Select test image
2. Configure test parameters (perspectives, iterations, workers)
3. Click **Run Benchmark**

## Camera Angles

- **Pitch**: 1-179° (60°=up, 90°=horizon, 120°=down)
- **Yaw**: 0-360° (0°=front, 90°=right, 180°=back, 270°=left)

Common presets:

- **360° Coverage**: pitch=`60,90,120` yaw=`0,60,120,180,240,300`
- **Horizon Views**: pitch=`90` yaw=`0,90,180,270`

## Output Files

Generated images are named: `{image_name}_pitch{pitch}_yaw{yaw}_fov{fov}.{format}`

Example: `panorama_pitch90_yaw0_fov100.jpg`

## Supported Formats

- **Input**: JPEG, PNG
- **Output**: JPEG, PNG, Auto (maintains original format)

## Troubleshooting

### Common Issues

**"No supported image files found"**

- Ensure images have .jpg, .jpeg, or .png extensions
- Check that the input directory contains image files

**Application won't start (macOS)**

- Right-click → "Open" on first run to bypass security warning

**Out of memory errors**

- Reduce number of worker threads
- Process smaller batches
- Use lower output resolution

**Slow performance**

- Increase worker threads (up to CPU core count)
- Use SSD storage for faster I/O
- Close other applications to free RAM

### Performance Tips

- **Workers**: Set to CPU core count for best performance
- **Memory**: Large images (>8K) may need fewer workers
- **Storage**: SSD significantly improves processing speed

## System Requirements

- **macOS**: 10.14+ (for pre-built executable)
- **RAM**: 4GB minimum, 8GB+ recommended
- **Storage**: 200MB + space for output images

## Version History

- **v0.0.1**: Initial release with GUI interface, parallel processing, and benchmarking tools
