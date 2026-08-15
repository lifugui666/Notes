import cv2
import numpy as np
import pytesseract
from PIL import Image

filename = './test.png'
img = Image.open(filename)
result = pytesseract.image_to_string(img,lang='eng') #使用简体中文解析图片
print(f'中文识别结果：\n {result}')