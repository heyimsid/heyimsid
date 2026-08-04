from rembg import remove
from PIL import Image
import cv2
import numpy as np
import os
import sys


def remove_background(img):
    return remove(img)


def clahe(gray):
    clahe_filter = cv2.createCLAHE(
        clipLimit=2.5,
        tileGridSize=(8, 8)
    )
    return clahe_filter.apply(gray)


def main(image_path):

    if not os.path.exists(image_path):
        print("Image not found.")
        return

    print("Loading image...")

    pil = Image.open(image_path).convert("RGBA")

    print("Removing background...")

    cutout = remove_background(pil)

    arr = np.array(cutout)

    rgb = arr[:, :, :3]

    alpha = arr[:, :, 3]

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    print("Applying CLAHE...")

    gray = clahe(gray)

    white = np.full_like(gray, 255)

    result = np.where(alpha > 0, gray, white)

    out = Image.fromarray(result)

    os.makedirs("assets", exist_ok=True)

    output = "assets/profile-prepped.png"

    out.save(output)

    print()
    print("Done.")
    print(output)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage:")
        print("python scripts/prep_photo.py assets/profile.png")
    else:
        main(sys.argv[1])