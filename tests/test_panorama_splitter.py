import os
import pytest
import numpy as np
from PIL import Image
import tempfile
import shutil

from pano_splitter import (
    PanoramaImage,
    PerspectiveImage,
    PerspectiveMetadata,
    DEFAULT_IMAGE_PERSPECTIVES,
    ZOOMED_IN_IMAGE_PERSPECTIVES,
    ZOOMED_OUT_IMAGE_PERSPECTIVES,
)


class TestPanoramaSplitter:
    """Test suite for the panorama splitter functionality."""

    @pytest.fixture
    def sample_panorama_path(self):
        """Fixture that provides the path to the test panorama image."""
        return "tests/test_pano.jpg"

    @pytest.fixture
    def temp_output_dir(self):
        """Fixture that creates a temporary directory for test outputs."""
        temp_dir = tempfile.mkdtemp(prefix="pano_test_")
        yield temp_dir
        # Clean up after test
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_panorama_array(self):
        """Fixture that creates a synthetic panorama image for testing."""
        # Create a simple synthetic equirectangular panorama
        width, height = 1024, 512
        panorama = np.zeros((height, width, 3), dtype=np.uint8)

        # Add some patterns to make it more realistic
        # Horizontal gradient
        for x in range(width):
            panorama[:, x, 0] = int((x / width) * 255)

        # Vertical gradient
        for y in range(height):
            panorama[y, :, 1] = int((y / height) * 255)

        # Some geometric patterns
        center_y, center_x = height // 2, width // 2
        y_coords, x_coords = np.ogrid[:height, :width]

        # Add circular patterns
        distance = np.sqrt((x_coords - center_x) ** 2 + (y_coords - center_y) ** 2)
        panorama[:, :, 2] = np.clip(np.sin(distance / 20) * 127 + 128, 0, 255).astype(
            np.uint8
        )

        return panorama

    def test_perspective_metadata_creation(self):
        """Test creating perspective metadata objects."""
        metadata = PerspectiveMetadata(
            pixel_width=512,
            pixel_height=512,
            horizontal_fov=45.0,
            vertical_fov=45.0,
            yaw_offset=0.0,
            pitch_offset=0.0,
        )

        assert metadata.pixel_width == 512
        assert metadata.pixel_height == 512
        assert metadata.horizontal_fov == 45.0
        assert metadata.vertical_fov == 45.0
        assert metadata.yaw_offset == 0.0
        assert metadata.pitch_offset == 0.0

    def test_panorama_image_from_array(self, sample_panorama_array):
        """Test creating a PanoramaImage from a numpy array."""
        panorama = PanoramaImage("test_pano", sample_panorama_array)

        assert panorama.panorama_id == "test_pano"
        assert panorama.loaded_image_array is not None
        assert panorama.loaded_image is not None
        assert panorama.loaded_image_array.shape == sample_panorama_array.shape

    def test_perspective_image_generation(self, sample_panorama_array):
        """Test generating a perspective image from a panorama."""
        panorama = PanoramaImage("test_pano", sample_panorama_array)

        # Create a perspective metadata
        perspective_metadata = PerspectiveMetadata(
            pixel_width=256,
            pixel_height=256,
            horizontal_fov=45.0,
            vertical_fov=45.0,
            yaw_offset=0.0,
            pitch_offset=0.0,
        )

        # Generate perspective image
        perspective_image = panorama.generate_perspective_image(perspective_metadata)

        assert isinstance(perspective_image, PerspectiveImage)
        assert perspective_image.panorama_id == "test_pano"
        assert perspective_image.perspective_metadata == perspective_metadata
        assert perspective_image.perspective_image_array is not None
        assert perspective_image.perspective_image is not None
        assert perspective_image.perspective_image_array.shape[:2] == (256, 256)

    def test_multiple_perspectives_generation(self, sample_panorama_array):
        """Test generating multiple perspective views from a single panorama."""
        panorama = PanoramaImage("test_pano", sample_panorama_array)

        # Use a subset of default perspectives for faster testing
        test_perspectives = DEFAULT_IMAGE_PERSPECTIVES[:4]  # Test first 4 perspectives

        perspective_images = []
        for perspective_metadata in test_perspectives:
            perspective_image = panorama.generate_perspective_image(
                perspective_metadata
            )
            perspective_images.append(perspective_image)

            # Verify each perspective image
            assert isinstance(perspective_image, PerspectiveImage)
            assert perspective_image.perspective_image_array is not None
            assert perspective_image.perspective_image_array.shape[:2] == (
                perspective_metadata.pixel_height,
                perspective_metadata.pixel_width,
            )

        assert len(perspective_images) == 4

    def test_panorama_splitting_with_real_image(
        self, sample_panorama_path, temp_output_dir
    ):
        """Test splitting the real panorama image with proper cleanup."""
        if not os.path.exists(sample_panorama_path):
            pytest.skip(f"Test panorama image not found at {sample_panorama_path}")

        # Load the panorama
        panorama = PanoramaImage("test_pano", sample_panorama_path)

        # Generate a few perspective views using different configurations
        test_configs = [
            ("default", DEFAULT_IMAGE_PERSPECTIVES[:3]),
            ("zoomed_in", ZOOMED_IN_IMAGE_PERSPECTIVES[:2]),
        ]

        total_generated = 0
        for config_name, perspectives in test_configs:
            config_dir = os.path.join(temp_output_dir, config_name)
            os.makedirs(config_dir, exist_ok=True)

            for i, perspective_metadata in enumerate(perspectives):
                perspective_image = panorama.generate_perspective_image(
                    perspective_metadata
                )

                # Create descriptive filename
                filename = f"{config_name}_perspective_{i:02d}_{perspective_metadata.to_file_suffix()}.jpg"
                output_path = os.path.join(config_dir, filename)

                perspective_image.perspective_image.save(
                    output_path, "JPEG", quality=90
                )
                total_generated += 1

                # Verify file was created
                assert os.path.exists(output_path)

                # Verify we can load it back
                loaded_img = Image.open(output_path)
                assert loaded_img.size == (
                    perspective_metadata.pixel_width,
                    perspective_metadata.pixel_height,
                )

        assert total_generated == 5  # 3 + 2
        print(
            f"✅ Generated {total_generated} test images in temporary directory: {temp_output_dir}"
        )


def test_constants_perspective_configurations():
    """Test that the predefined perspective configurations are valid."""
    # Test DEFAULT_IMAGE_PERSPECTIVES
    assert len(DEFAULT_IMAGE_PERSPECTIVES) > 0
    for perspective in DEFAULT_IMAGE_PERSPECTIVES:
        assert isinstance(perspective, PerspectiveMetadata)
        assert perspective.horizontal_fov > 0
        assert perspective.vertical_fov > 0
        assert perspective.pixel_width > 0
        assert perspective.pixel_height > 0

    # Test ZOOMED_IN_IMAGE_PERSPECTIVES
    assert len(ZOOMED_IN_IMAGE_PERSPECTIVES) > 0
    for perspective in ZOOMED_IN_IMAGE_PERSPECTIVES:
        assert isinstance(perspective, PerspectiveMetadata)

    # Test ZOOMED_OUT_IMAGE_PERSPECTIVES
    assert len(ZOOMED_OUT_IMAGE_PERSPECTIVES) > 0
    for perspective in ZOOMED_OUT_IMAGE_PERSPECTIVES:
        assert isinstance(perspective, PerspectiveMetadata)


if __name__ == "__main__":
    # Only show how to run tests, don't create files
    print("To run tests: uv run pytest tests/ -v")
    print(
        "To run specific test: uv run pytest tests/test_panorama_splitter.py::test_constants_perspective_configurations -v"
    )
