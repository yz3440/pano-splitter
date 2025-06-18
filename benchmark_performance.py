#!/usr/bin/env python3
"""
Benchmark script to compare sequential vs parallel processing performance
"""

import argparse
import time
from pathlib import Path
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

from pano_splitter.models import PanoramaImage, PerspectiveMetadata


def benchmark_sequential(image_path: str, perspectives: list, iterations: int = 1):
    """Benchmark sequential processing"""
    print(f"🔄 Running sequential benchmark ({iterations} iteration(s))...")

    total_time = 0
    total_images = 0

    for i in range(iterations):
        start_time = time.time()

        for perspective_metadata in perspectives:
            panorama = PanoramaImage(panorama_id="benchmark", image=image_path)
            perspective_image = panorama.generate_perspective_image(
                perspective_metadata
            )
            # Simulate saving by getting the array
            _ = perspective_image.get_perspective_image_array()
            total_images += 1

        elapsed = time.time() - start_time
        total_time += elapsed
        print(
            f"  Iteration {i+1}: {elapsed:.2f}s, {len(perspectives)/elapsed:.2f} imgs/sec"
        )

    avg_time = total_time / iterations
    avg_rate = total_images / total_time

    print(f"📊 Sequential Average: {avg_time:.2f}s, {avg_rate:.2f} imgs/sec")
    return avg_time, avg_rate


def benchmark_parallel(
    image_path: str, perspectives: list, max_workers: int, iterations: int = 1
):
    """Benchmark parallel processing"""
    print(
        f"⚡ Running parallel benchmark with {max_workers} workers ({iterations} iteration(s))..."
    )

    total_time = 0
    total_images = 0

    for i in range(iterations):
        start_time = time.time()

        # Load image once
        panorama = PanoramaImage(panorama_id="benchmark", image=image_path)

        # Generate perspectives in parallel using batch method
        perspective_images = panorama.generate_perspective_images_batch(
            perspectives, max_workers=max_workers
        )

        # Simulate saving
        for perspective_image in perspective_images:
            _ = perspective_image.get_perspective_image_array()
            total_images += 1

        elapsed = time.time() - start_time
        total_time += elapsed
        print(
            f"  Iteration {i+1}: {elapsed:.2f}s, {len(perspectives)/elapsed:.2f} imgs/sec"
        )

    avg_time = total_time / iterations
    avg_rate = total_images / total_time

    print(f"📊 Parallel Average: {avg_time:.2f}s, {avg_rate:.2f} imgs/sec")
    return avg_time, avg_rate


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark sequential vs parallel panorama processing"
    )

    parser.add_argument(
        "--input_image", type=str, required=True, help="Path to test panorama image"
    )

    parser.add_argument(
        "--output_width", type=int, default=1000, help="Output image width"
    )

    parser.add_argument(
        "--output_height", type=int, default=1500, help="Output image height"
    )

    parser.add_argument("--fov", type=int, default=90, help="Field of view")

    parser.add_argument(
        "--num_perspectives",
        type=int,
        default=12,
        help="Number of perspective views to generate (default: 12 = 2 pitches × 6 yaws)",
    )

    parser.add_argument(
        "--max_workers",
        type=int,
        default=None,
        help="Maximum number of parallel workers (default: auto-detect)",
    )

    parser.add_argument(
        "--iterations", type=int, default=3, help="Number of benchmark iterations"
    )

    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.input_image)
    if not input_path.exists():
        print(f"❌ Error: Input image '{input_path}' does not exist.")
        return

    # Set up test perspectives
    pitch_angles = [60, 120]  # 2 pitches
    yaw_angles = [0, 60, 120, 180, 240, 300]  # 6 yaws

    perspectives = []
    count = 0
    for pitch_angle in pitch_angles:
        for yaw_angle in yaw_angles:
            if count >= args.num_perspectives:
                break

            adjusted_pitch = (180 - pitch_angle) - 90  # Convert coordinate system

            perspective = PerspectiveMetadata(
                pixel_width=args.output_width,
                pixel_height=args.output_height,
                horizontal_fov=args.fov,
                vertical_fov=args.fov,
                yaw_offset=yaw_angle,
                pitch_offset=adjusted_pitch,
            )
            perspectives.append(perspective)
            count += 1

        if count >= args.num_perspectives:
            break

    print(f"🎯 Benchmark Configuration:")
    print(f"   Input: {input_path.name}")
    print(f"   Perspectives: {len(perspectives)}")
    print(f"   Output size: {args.output_width}x{args.output_height}")
    print(f"   FOV: {args.fov}°")
    print(f"   Iterations: {args.iterations}")
    print(f"   CPU cores: {multiprocessing.cpu_count()}")
    print(f"   Max workers: {args.max_workers or 'auto'}")
    print()

    # Run benchmarks
    seq_time, seq_rate = benchmark_sequential(
        str(input_path), perspectives, args.iterations
    )

    print()

    par_time, par_rate = benchmark_parallel(
        str(input_path), perspectives, args.max_workers, args.iterations
    )

    # Calculate speedup
    speedup = seq_time / par_time
    throughput_improvement = par_rate / seq_rate

    print(f"\n🏁 Benchmark Results:")
    print(f"   Sequential: {seq_time:.2f}s ({seq_rate:.2f} imgs/sec)")
    print(f"   Parallel:   {par_time:.2f}s ({par_rate:.2f} imgs/sec)")
    print(f"   Speedup:    {speedup:.2f}x")
    print(f"   Throughput: {throughput_improvement:.2f}x improvement")

    if speedup > 1.5:
        print(f"🚀 Excellent speedup! Parallel processing is {speedup:.1f}x faster")
    elif speedup > 1.1:
        print(f"✅ Good speedup! Parallel processing is {speedup:.1f}x faster")
    else:
        print(
            f"⚠️  Limited speedup. Consider using fewer workers or check if the workload is suitable for parallelization"
        )


if __name__ == "__main__":
    main()
