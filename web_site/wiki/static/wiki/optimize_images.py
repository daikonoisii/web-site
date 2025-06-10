import os

from PIL import Image


def optimize_image(
    input_path, output_path=None, quality=85
):
    """
    Optimize an image file
    :param input_path: Path to the input image
    :param output_path: Path to save the optimized image (if None, overwrites the input)
    :param quality: JPEG quality (1-100)
    """
    if output_path is None:
        output_path = input_path

    try:
        img = Image.open(input_path)

        # Convert to RGB if the image is in RGBA mode
        if img.mode in ("RGBA", "LA"):
            background = Image.new(
                "RGB", img.size, (255, 255, 255)
            )
            background.paste(img, mask=img.split()[-1])
            img = background

        # Save the optimized image
        img.save(
            output_path,
            "JPEG",
            quality=quality,
            optimize=True,
        )
        print(f"Optimized: {input_path}")
    except Exception as e:
        print(f"Error optimizing {input_path}: {str(e)}")


def main():
    # Directory containing images
    current_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(current_dir, "img")

    # Process all image files
    for filename in os.listdir(img_dir):
        if filename.lower().endswith(
            (".png", ".jpg", ".jpeg")
        ):
            input_path = os.path.join(img_dir, filename)
            optimize_image(input_path)


if __name__ == "__main__":
    main()
