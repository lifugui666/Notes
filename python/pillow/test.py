import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from PIL import ImageFilter

# 打开图片，旋转，然后保存旋转后的副本，用于之后的图片加减
def open_save_file():
    image = Image.open("./qitingzhang.jpg")
    rotated_image = image.rotate(180)
    small_image = image.resize((64, 64))
    rotated_image.save("ro_qitingzhang.jpg")
    small_image.save("./small_qitingzhang.jpg")

def split_rgb():
    image = Image.open("./qitingzhang.jpg")
    img_r, img_g, img_b = image.split()
   
    plt.subplot(221)
    plt.axis("off")
    plt.imshow(image)

    plt.subplot(222)
    plt.axis("off")
    plt.imshow(img_r)
    
    plt.subplot(223)
    plt.axis("off")
    plt.imshow(img_g)
    
    plt.subplot(224)
    plt.axis("off")
    plt.imshow(img_b)

    plt.show()

def append_noise_and_filter():
    # 对图片添加噪声
    image = Image.open("./qitingzhang.jpg")
    img_array = np.array(image)
    h, w, c = img_array.shape
    noise_array = np.random.normal(0, 25, (h,w,c))
    noisy_img_array = np.clip(img_array + noise_array, 0, 255).astype(np.uint8)
    noisy_img = Image.fromarray(noisy_img_array)
    # 使用pillow自带的滤波进行高斯滤波
    after_filter_img = noisy_img.filter(ImageFilter.GaussianBlur(radius = 2))

    plt.subplot(131)
    plt.axis("off")
    plt.imshow(image)

    plt.subplot(132)
    plt.axis("off")
    plt.imshow(noisy_img)
    
    plt.subplot(133)
    plt.axis("off")
    plt.imshow(after_filter_img)

    plt.show()

def add_and_sub():
    image1 = Image.open("./qitingzhang.jpg")
    image2 = Image.open("./ro_qitingzhang.jpg")
    
    image1_array = np.array(image1)
    image2_array = np.array(image2)

    add_result_array = image1_array + image2_array
    sub_result_array = np.abs(image1_array - image2_array)

    add_result_img = Image.fromarray(add_result_array)
    sub_result_img = Image.fromarray(sub_result_array)
    
    plt.subplot(121)
    plt.axis("off")
    plt.imshow(add_result_img)

    plt.subplot(122)
    plt.axis("off")
    plt.imshow(sub_result_img)

    plt.show()

open_save_file()
split_rgb()
append_noise_and_filter()
add_and_sub()


