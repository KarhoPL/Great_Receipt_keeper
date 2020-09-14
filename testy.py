from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import pandas as pd
import csv
import numpy as np
import sys
import codecs

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\kharacz\AppData\Local\Tesseract-OCR\tesseract.exe'
#funkcja zwracająca listę zakupów z zdjecia paragonu
im = Image.open('paragon_2.jpg')
im = im.filter(ImageFilter.MedianFilter())
enhancer = ImageEnhance.Contrast(im)
#im = enhancer.enhance(2)
#im = im.convert('1')
im = im.rotate(270)
im.save('unnamed2.jpg')
lines =  (pytesseract.image_to_string(Image.open('unnamed2.jpg'))).split("\n")
for line in lines:
    print(line)