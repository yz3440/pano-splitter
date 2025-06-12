# Pano Splitter

A Python library for converting equirectangular panoramic images into perspective views. This tool takes 360° panoramic images and generates multiple perspective images with configurable field of view, resolution, and viewing angles.

## Features

- Convert equirectangular panoramas to perspective views
- Configurable FOV, resolution, and viewing angles
- Pre-configured perspective sets
- Fast OpenCV-based processing

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency management. Make sure you have `uv` installed first.

```bash
# Clone the repository
git clone https://github.com/yz3440/pano-splitter.git
cd pano-splitter

# Install dependencies
uv sync

# Install in development mode
uv pip install -e .
```

## Quick Start

```python
from pano_splitter import PanoramaImage, PerspectiveMetadata, DEFAULT_IMAGE_PERSPECTIVES

# Load a panoramic image
panorama = PanoramaImage("my_pano", "path/to/panorama.jpg")

# Create a custom perspective configuration
perspective_config = PerspectiveMetadata(
    pixel_width=1024,
    pixel_height=1024,
    horizontal_fov=60.0,  # degrees
    vertical_fov=60.0,    # degrees
    yaw_offset=0.0,       # horizontal rotation
    pitch_offset=0.0      # vertical rotation
)

# Generate perspective image
perspective_image = panorama.generate_perspective_image(perspective_config)

# Save the result
perspective_image.perspective_image.save("output.jpg")
```

## Usage Examples

### Using Pre-configured Perspective Sets

The library comes with several pre-configured perspective sets:

```python
from pano_splitter import (
    PanoramaImage,
    DEFAULT_IMAGE_PERSPECTIVES,
    ZOOMED_IN_IMAGE_PERSPECTIVES,
    ZOOMED_OUT_IMAGE_PERSPECTIVES,
    ZOOMED_OUT_IMAGE_PERSPECTIVES_60
)

panorama = PanoramaImage("sample", "panorama.jpg")

# Generate multiple perspectives using default configuration
# (45° FOV, 2048x2048 pixels, 22.5° intervals around 360°)
for i, perspective in enumerate(DEFAULT_IMAGE_PERSPECTIVES):
    perspective_image = panorama.generate_perspective_image(perspective)
    perspective_image.perspective_image.save(f"perspective_{i:02d}.jpg")
```

### Custom Perspective Configuration

```python
from pano_splitter import PanoramaImage, PerspectiveMetadata

# Load panorama
panorama = PanoramaImage("custom", "my_panorama.jpg")

# Create custom perspectives
perspectives = []

# Front view
perspectives.append(PerspectiveMetadata(
    pixel_width=1920, pixel_height=1080,
    horizontal_fov=90, vertical_fov=60,
    yaw_offset=0, pitch_offset=0
))

# Right view
perspectives.append(PerspectiveMetadata(
    pixel_width=1920, pixel_height=1080,
    horizontal_fov=90, vertical_fov=60,
    yaw_offset=90, pitch_offset=0
))

# Generate images
for i, perspective in enumerate(perspectives):
    image = panorama.generate_perspective_image(perspective)
    image.perspective_image.save(f"custom_view_{i}.jpg")
```

### Working with NumPy Arrays

```python
import numpy as np
from pano_splitter import PanoramaImage, PerspectiveMetadata

# Load from numpy array
panorama_array = np.array(Image.open("panorama.jpg"))
panorama = PanoramaImage("from_array", panorama_array)

# Generate perspective
perspective = PerspectiveMetadata(512, 512, 45, 45, 0, 0)
result = panorama.generate_perspective_image(perspective)

# Access as numpy array
perspective_array = result.perspective_image_array
print(f"Generated perspective shape: {perspective_array.shape}")
```

## Pre-configured Perspective Sets

| Configuration                      | FOV   | Resolution | Count | Description                            |
| ---------------------------------- | ----- | ---------- | ----- | -------------------------------------- |
| `DEFAULT_IMAGE_PERSPECTIVES`       | 45°   | 2048×2048  | 16    | Standard perspective views every 22.5° |
| `ZOOMED_IN_IMAGE_PERSPECTIVES`     | 22.5° | 1024×1024  | 32    | High-detail zoomed views every 11.25°  |
| `ZOOMED_OUT_IMAGE_PERSPECTIVES`    | 90°   | 2500×2500  | 8     | Wide-angle views every 45°             |
| `ZOOMED_OUT_IMAGE_PERSPECTIVES_60` | 60°   | 2500×2500  | 12    | Medium-wide views every 30°            |

## API Reference

### Classes

#### `PanoramaImage`

Main class for handling panoramic images.

```python
PanoramaImage(panorama_id: str, image: Union[str, Image.Image, np.ndarray])
```

- `panorama_id`: Unique identifier for the panorama
- `image`: Input image (file path, PIL Image, or NumPy array)

**Methods:**

- `generate_perspective_image(perspective: PerspectiveMetadata) -> PerspectiveImage`

#### `PerspectiveMetadata`

Configuration for perspective image generation.

```python
PerspectiveMetadata(
    pixel_width: int,
    pixel_height: int,
    horizontal_fov: float,
    vertical_fov: float,
    yaw_offset: float,
    pitch_offset: float
)
```

#### `PerspectiveImage`

Generated perspective image with metadata.

**Properties:**

- `perspective_image`: PIL Image object
- `perspective_image_array`: NumPy array
- `perspective_metadata`: Associated metadata
- `panorama_id`: Source panorama identifier

## Technical Details

### Coordinate System

- **Yaw (horizontal)**: -180° to +180° (left to right)
- **Pitch (vertical)**: -90° to +90° (down to up)
- **FOV**: Field of view in degrees

### Image Processing

- Uses equirectangular to perspective projection
- Bilinear interpolation for smooth results
- OpenCV-based implementation for performance
- Supports RGB images

## Testing

Run the test suite:

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test
uv run pytest tests/test_panorama_splitter.py::test_constants_perspective_configurations -v

# Run with coverage
uv run pytest tests/ --cov=pano_splitter
```

## Requirements

- Python ≥ 3.8
- NumPy ≥ 1.20.0
- OpenCV ≥ 4.5.0
- Pillow ≥ 8.0.0

## License

MIT
