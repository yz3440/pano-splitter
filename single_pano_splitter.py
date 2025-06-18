#!/usr/bin/env python3
"""
Single Panorama to Planar Image Converter using pano_splitter implementation

This script converts a single 360-degree panoramic image into planar images using the
same API as the original single_image.py but with improved performance using OpenCV
and parallel processing for better performance.
"""

import argparse
from pathlib import Path
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import List, Tuple

from pano_splitter.models import PanoramaImage, PerspectiveMetadata


def check_pitch(value):
    """Validate pitch value is between 1 and 179 degrees."""
    ivalue = int(value)
    if ivalue < 1 or ivalue > 179:
        raise argparse.ArgumentTypeError(
            f"{value} is an invalid pitch value. It must be between 1 and 179."
        )
    return ivalue


def check_pitch_list(values: list[int]):
    """Validate pitch values are between 1 and 179 degrees."""
    for val in values:
        if val < 1 or val > 179:
            raise argparse.ArgumentTypeError(
                f"{val} is an invalid pitch value. It must be between 1 and 179."
            )


def check_yaw(values: list[int]):
    """Validate yaw values are between 0 and 360 degrees."""
    for val in values:
        if val < 0 or val > 360:
            raise argparse.ArgumentTypeError(
                f"{val} is an invalid yaw value. It must be between 0 and 360."
            )


def process_single_perspective(
    panorama_array: np.ndarray,
    panorama_id: str,
    FOV: int,
    output_size: tuple,
    yaw: float,
    pitch: float,
    output_path: Path,
    output_format: str,
    pitch_angle: int,
) -> Tuple[bool, str]:
    """
    Process a single perspective view of a panorama.

    Args:
        panorama_array: Pre-loaded panorama image array
        panorama_id: ID of the panorama
        FOV: Field of view in degrees
        output_size: (width, height) tuple for output image
        yaw: Yaw angle in degrees
        pitch: Pitch angle in degrees
        output_path: Output directory path
        output_format: Output file format
        pitch_angle: Original pitch angle for filename

    Returns:
        Tuple of (success, filename)
    """
    try:
        # Create panorama object from array (avoiding file I/O)
        panorama = PanoramaImage(panorama_id=panorama_id, image=panorama_array)

        # Create perspective metadata
        adjusted_pitch = pitch - 90  # Convert from original coordinate system

        perspective_metadata = PerspectiveMetadata(
            pixel_width=output_size[0],
            pixel_height=output_size[1],
            horizontal_fov=FOV,
            vertical_fov=FOV,
            yaw_offset=yaw,
            pitch_offset=adjusted_pitch,
        )

        # Generate perspective image
        perspective_image = panorama.generate_perspective_image(perspective_metadata)
        output_image_array = perspective_image.get_perspective_image_array()

        # Generate output image name
        output_image_name = (
            f"{panorama_id}_pitch{pitch_angle}_yaw{yaw}_fov{FOV}.{output_format}"
        )
        output_image_path = output_path / output_image_name

        # Save the image using OpenCV
        output_image_bgr = cv2.cvtColor(output_image_array, cv2.COLOR_RGB2BGR)
        success = cv2.imwrite(str(output_image_path), output_image_bgr)

        return success, output_image_name

    except Exception as e:
        return False, f"Error processing pitch {pitch_angle}, yaw {yaw}: {str(e)}"


def main():
    # Create the parser
    parser = argparse.ArgumentParser(
        description="Convert a single 360-degree panoramic image to planar images using pano_splitter with parallel processing."
    )

    # Add arguments - exactly the same as original single_image.py
    parser.add_argument(
        "--input_image",
        type=str,
        help="Path to the input panorama image",
        required=True,
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default="output_image",
        help="Path to the output images",
    )
    parser.add_argument(
        "--output_format",
        type=str,
        choices=["png", "jpg", "jpeg"],
        help='Output image format - "png", "jpg", "jpeg"',
    )
    parser.add_argument("--FOV", type=int, default=100, help="Field of View")
    parser.add_argument(
        "--output_width", type=int, default=1000, help="Width of the output image"
    )
    parser.add_argument(
        "--output_height", type=int, default=1500, help="Height of the output image"
    )
    parser.add_argument(
        "--pitch",
        type=int,
        default=90,
        help="Pitch angle (vertical). Must be between 1 and 179.",
    )
    parser.add_argument(
        "--list-of-pitch",
        nargs="+",
        type=int,
        help="List of pitch angles (vertical) e.g. --list-of-pitch 60 90 120. Takes precedence over --pitch if provided.",
    )
    parser.add_argument(
        "--list-of-yaw",
        nargs="+",
        type=int,
        default=[0, 60, 120, 180, 240, 300],
        help="List of yaw angles (horizontal) e.g. --list-of-yaw 0 60 120 180 240 300",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help="Maximum number of worker threads for parallel processing (default: auto-detect)",
    )

    # Parse the arguments
    args = parser.parse_args()

    # Determine pitch list (use list-of-pitch if provided, otherwise use single pitch)
    if args.list_of_pitch:
        check_pitch_list(args.list_of_pitch)
        pitch_list = args.list_of_pitch
    else:
        check_pitch(args.pitch)
        pitch_list = [args.pitch]

    # Validate yaw arguments
    check_yaw(args.list_of_yaw)

    # Accessing argument values
    FOV = args.FOV
    output_size = (args.output_width, args.output_height)
    yaw_list = args.list_of_yaw
    output_format = args.output_format

    # Set up paths
    input_image = Path(args.input_image)
    output_path = Path(args.output_path)

    # Validate input image exists
    if not input_image.exists():
        print(f"❌ Error: Input image '{input_image}' does not exist.")
        return

    # Create output directory if it doesn't exist
    if not output_path.exists():
        output_path.mkdir(parents=True)

    # Process single image
    file_name = input_image.stem  # Extract file name without extension

    # Determine output format
    if args.output_format is None:
        current_output_format = input_image.suffix[1:].lower()
    else:
        current_output_format = output_format

    print(f"📷 Processing: {input_image.name}")
    print(f"📤 Output directory: {output_path}")
    print(f"⚙️  Parameters: FOV={FOV}, pitch_angles={pitch_list}, yaw_angles={yaw_list}")
    print(f"📏 Output size: {args.output_width}x{args.output_height}")
    print(f"🔧 Max workers: {args.max_workers or 'auto'}")

    start_time = time.time()

    # Load the panorama image once
    try:
        panorama_image = cv2.imread(str(input_image))
        panorama_array = cv2.cvtColor(panorama_image, cv2.COLOR_BGR2RGB)
    except Exception as e:
        print(f"❌ Failed to load image: {str(e)}")
        return

    # Create list of all perspective tasks
    tasks = []
    for pitch_angle in pitch_list:
        for yaw in yaw_list:
            pitch = 180 - pitch_angle  # Convert to original coordinate system
            tasks.append((pitch_angle, yaw, pitch))

    print(f"🎯 Generating {len(tasks)} perspective views...")
    processed_count = 0

    # Process perspectives in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        # Submit all tasks
        future_to_task = {}
        for pitch_angle, yaw, pitch in tasks:
            future = executor.submit(
                process_single_perspective,
                panorama_array,
                file_name,
                FOV,
                output_size,
                yaw,
                pitch,
                output_path,
                current_output_format,
                pitch_angle,
            )
            future_to_task[future] = (pitch_angle, yaw)

        # Collect results
        for future in as_completed(future_to_task):
            pitch_angle, yaw = future_to_task[future]
            try:
                success, result = future.result()
                if success:
                    print(f"  ✓ Saved: {result}")
                    processed_count += 1
                else:
                    print(f"  ✗ {result}")
            except Exception as e:
                print(f"  ✗ Error processing pitch {pitch_angle}, yaw {yaw}: {str(e)}")

    elapsed_time = time.time() - start_time

    print(f"\n🎉 Processing complete!")
    print(
        f"📊 Generated {processed_count}/{len(tasks)} images from '{input_image.name}'"
    )
    print(f"⏱️  Total time: {elapsed_time:.2f} seconds")
    print(f"🚀 Average: {processed_count/elapsed_time:.2f} images/second")

    if processed_count == 0:
        print("\n❌ No images were processed. Please check:")
        print("- Input image path is correct and file exists")
        print("- Input image is a valid panoramic image format (.jpg, .jpeg, .png)")
        print("- You have write permissions to the output directory")


if __name__ == "__main__":
    main()
