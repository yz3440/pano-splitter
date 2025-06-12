#!/usr/bin/env python3
"""
Single Panorama to Planar Image Converter using pano_splitter implementation

This script converts a single 360-degree panoramic image into planar images using the
same API as the original single_image.py but with improved performance using OpenCV.
"""

import argparse
from pathlib import Path
import cv2
import numpy as np

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


def panorama_to_plane(
    panorama_path: str, FOV: int, output_size: tuple, yaw: float, pitch: float
) -> np.ndarray:
    """
    Convert panorama to planar image using pano_splitter implementation.

    Args:
        panorama_path: Path to the panorama image
        FOV: Field of view in degrees
        output_size: (width, height) tuple for output image
        yaw: Yaw angle in degrees
        pitch: Pitch angle in degrees (adjusted from original coordinate system)

    Returns:
        Perspective image as numpy array
    """
    # Load the panorama image
    panorama = PanoramaImage(panorama_id=Path(panorama_path).stem, image=panorama_path)

    # Create perspective metadata
    # Note: The original implementation uses pitch differently, so we adjust here
    # Original: pitch=90 is looking straight ahead, pitch=180-90=90 is used in calculation
    # Our implementation: pitch=0 is looking straight ahead
    adjusted_pitch = pitch - 90  # Convert from original coordinate system

    perspective_metadata = PerspectiveMetadata(
        pixel_width=output_size[0],
        pixel_height=output_size[1],
        horizontal_fov=FOV,
        vertical_fov=FOV,  # Use same FOV for both dimensions
        yaw_offset=yaw,
        pitch_offset=adjusted_pitch,
    )

    # Generate perspective image
    perspective_image = panorama.generate_perspective_image(perspective_metadata)

    return perspective_image.get_perspective_image_array()


def main():
    # Create the parser
    parser = argparse.ArgumentParser(
        description="Convert a single 360-degree panoramic image to planar images using pano_splitter."
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

    print(f"Processing: {input_image.name}")
    print(f"Output directory: {output_path}")
    print(f"Parameters: FOV={FOV}, pitch_angles={pitch_list}, yaw_angles={yaw_list}")
    print(f"Output size: {args.output_width}x{args.output_height}")

    processed_count = 0

    for pitch_angle in pitch_list:
        for yaw in yaw_list:
            try:
                # Convert to original coordinate system for internal calculations
                pitch = 180 - pitch_angle

                # Generate output image name (same format as original)
                output_image_name = f"{file_name}_pitch{pitch_angle}_yaw{yaw}_fov{FOV}.{current_output_format}"
                output_image_path = output_path / output_image_name

                # Convert panorama to planar image
                output_image_array = panorama_to_plane(
                    str(input_image), FOV, output_size, yaw, pitch
                )

                # Save the image using OpenCV (faster than PIL)
                # Convert RGB to BGR for OpenCV
                output_image_bgr = cv2.cvtColor(output_image_array, cv2.COLOR_RGB2BGR)
                success = cv2.imwrite(str(output_image_path), output_image_bgr)

                if success:
                    print(f"  ✓ Saved: {output_image_name}")
                    processed_count += 1
                else:
                    print(f"  ✗ Failed to save: {output_image_name}")

            except Exception as e:
                print(f"  ✗ Error processing pitch {pitch_angle}, yaw {yaw}: {str(e)}")
                continue

    print(
        f"\n🎉 Processing complete! Generated {processed_count} images from '{input_image.name}'."
    )
    if processed_count == 0:
        print("No images were processed. Please check:")
        print("- Input image path is correct and file exists")
        print("- Input image is a valid panoramic image format (.jpg, .jpeg, .png)")
        print("- You have write permissions to the output directory")


if __name__ == "__main__":
    main()
