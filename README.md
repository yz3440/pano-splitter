# Pano Splitter

High-performance panorama to planar image converter with parallel processing capabilities.

## Features

- **Fast OpenCV-based processing**: Optimized equirectangular to perspective projection
- **Parallel Processing**: Multi-threaded processing for significant performance improvements
- **Batch Processing**: Process multiple images and perspectives simultaneously
- **Memory Efficient**: Optimized image loading and reuse
- **Flexible Output**: Support for PNG, JPG, and JPEG formats
- **Performance Benchmarking**: Built-in tools to measure speedup

## Performance Improvements

The latest version includes significant performance optimizations:

### 🚀 Parallel Processing

- **Multi-threaded perspective generation**: Process multiple pitch/yaw combinations simultaneously
- **Batch image processing**: Handle multiple panorama images in parallel
- **Memory optimization**: Load each panorama image only once per processing session
- **Configurable worker threads**: Optimize for your system's capabilities

### 📊 Expected Performance Gains

- **2-4x speedup** on multi-core systems for typical workloads
- **Linear scaling** with number of CPU cores for compute-bound tasks
- **Reduced memory usage** through efficient image reuse
- **Better resource utilization** with balanced CPU and I/O operations

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or using uv (recommended)
uv sync
```

## Quick Start

### Process Multiple Images (Parallel)

```bash
python pano_splitter.py \
    --input_path ./input_images \
    --output_path ./output_images \
    --list-of-pitch 60 90 120 \
    --list-of-yaw 0 60 120 180 240 300 \
    --max-workers 8
```

### Process Single Image (Parallel)

```bash
python single_pano_splitter.py \
    --input_image ./my_panorama.jpg \
    --output_path ./output \
    --list-of-pitch 60 90 120 \
    --list-of-yaw 0 60 120 180 240 300 \
    --max-workers 8
```

### Benchmark Performance

```bash
python benchmark_performance.py \
    --input_image ./test_panorama.jpg \
    --num_perspectives 12 \
    --iterations 3
```

## Command Line Options

### Common Options

- `--max-workers`: Number of parallel worker threads (default: auto-detect)
- `--FOV`: Field of view in degrees (default: 90)
- `--output_width/--output_height`: Output image dimensions
- `--output_format`: Output format (png, jpg, jpeg)

### Perspective Configuration

- `--pitch`: Single pitch angle (1-179 degrees)
- `--list-of-pitch`: Multiple pitch angles (overrides --pitch)
- `--list-of-yaw`: Multiple yaw angles (default: [0, 60, 120, 180, 240, 300])

### Performance Tuning

- `--max-workers`: Control thread count for perspective processing
- `--max-image-workers`: Control process count for multi-image processing (pano_splitter.py only)

## Performance Optimization Tips

### 1. **Thread Count Selection**

```bash
# For CPU-intensive workloads
--max-workers $(nproc)

# For mixed CPU/I/O workloads
--max-workers $(($(nproc) * 2))

# Conservative (prevents system overload)
--max-workers $(($(nproc) / 2))
```

### 2. **Memory Considerations**

- Large panorama images benefit more from parallelization
- Monitor memory usage with many concurrent workers
- Consider reducing worker count for very large images

### 3. **I/O Performance**

- Use SSD storage for input/output when possible
- Batch processing reduces file I/O overhead
- Network storage may become bottleneck with many workers

## Benchmarking

The included benchmark script helps you find optimal settings:

```bash
# Quick benchmark
python benchmark_performance.py --input_image panorama.jpg

# Detailed benchmark with custom parameters
python benchmark_performance.py \
    --input_image panorama.jpg \
    --num_perspectives 24 \
    --iterations 5 \
    --max_workers 8
```

### Sample Benchmark Results

```
🏁 Benchmark Results:
   Sequential: 12.45s (2.41 imgs/sec)
   Parallel:   3.21s (9.35 imgs/sec)
   Speedup:    3.88x
   Throughput: 3.88x improvement
```

## Technical Details

### Parallelization Strategy

1. **Thread-level parallelism**: ThreadPoolExecutor for I/O-bound operations
2. **Image reuse**: Load panorama once, generate multiple perspectives
3. **Batch processing**: Process multiple images concurrently
4. **Memory optimization**: Efficient NumPy array handling

### Performance Characteristics

- **CPU-bound**: Perspective projection calculations
- **I/O-bound**: Image loading and saving
- **Memory-bound**: Large panorama image processing
- **Scalable**: Performance improves with CPU core count

## Migration from Sequential Version

The parallel version maintains full backward compatibility:

```bash
# Old way (still works)
python pano_splitter.py --input_path ./images --output_path ./output

# New way (with parallel processing)
python pano_splitter.py --input_path ./images --output_path ./output --max-workers 8
```

## System Requirements

- **Python 3.8+**
- **OpenCV**: For fast image processing
- **NumPy**: For numerical computations
- **PIL/Pillow**: For image I/O
- **Multi-core CPU**: For optimal parallel performance

## Contributing

Contributions welcome! Areas for improvement:

- GPU acceleration with CUDA/OpenCL
- Advanced scheduling algorithms
- Memory usage optimization
- Additional output formats

## License

[Add your license information here]
