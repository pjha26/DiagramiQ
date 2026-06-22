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
img_array = np.array(img.convert("RGB"))

gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

# save intermediate images for inspection
cv2.imwrite(r"E:\webd\DiagramiQ\debug_gray.png", gray)

_, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
cv2.imwrite(r"E:\webd\DiagramiQ\debug_thresh.png", thresh)

print(f"Gray min={gray.min()} max={gray.max()}")
print(f"Thresh non-zero={cv2.countNonZero(thresh)}")

# try RETR_TREE instead of RETR_EXTERNAL to find inner contours
contours, hierarchy = cv2.findContours(
    thresh,
    cv2.RETR_TREE,
    cv2.CHAIN_APPROX_SIMPLE
)

print(f"Total contours RETR_TREE: {len(contours)}")

sorted_c = sorted(contours, 
    key=lambda c: cv2.boundingRect(c)[2]*cv2.boundingRect(c)[3], 
    reverse=True)

for i, cnt in enumerate(sorted_c[:20]):
    x, y, w, h = cv2.boundingRect(cnt)
    area = w * h
    print(f"Contour {i}: x={x} y={y} w={w} h={h} area={area}")
