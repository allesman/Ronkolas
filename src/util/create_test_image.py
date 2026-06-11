"""
just 1 smol test image
"""

from PIL import Image

img = Image.new("RGB", (3, 3))
img.putdata([(0, 0, 0), (128, 128, 128), (255, 255, 255)] * 3)
img.save("Images_for_testing/test_3x3.bmp")
