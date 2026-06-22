import cv2
import numpy as np
from PIL import Image
import fitz
import io

pdf_path = r"E:\webd\DiagramiQ\Code Breaker.pdf"
with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

doc = fitz.open(stream=pdf_bytes, filetype="pdf")
page = doc[0]
mat = fitz.Matrix(3.0, 3.0)
pix = page.get_pixmap(matrix=mat)
img = Image.open(io.BytesIO(pix.tobytes("png")))

print(f"Image size: {img.size}")
print(f"Image mode: {img.mode}")

img_array = np.array(img.convert("RGB"))
gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
print(f"Gray min: {gray.min()}, max: {gray.max()}")

inverted = cv2.bitwise_not(gray)
_, thresh = cv2.threshold(inverted, 30, 255, cv2.THRESH_BINARY)
print(f"Thresh non-zero pixels: {cv2.countNonZero(thresh)}")

kernel = np.ones((15, 15), np.uint8)
dilated = cv2.dilate(thresh, kernel, iterations=3)

contours, _ = cv2.findContours(
    dilated,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)

print(f"Total contours found: {len(contours)}")
for i, cnt in enumerate(contours):
    x, y, w, h = cv2.boundingRect(cnt)
    area = w * h
    print(f"Contour {i}: x={x} y={y} w={w} h={h} area={area}")
