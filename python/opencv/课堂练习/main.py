import cv2
import numpy as np
import matplotlib.pyplot as plt

ori_file_path = "./pic.jpg"

def show_image(desc, image):
    cv2.imshow(desc, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

small_size=(240, 320)

# 轮廓检测
def check_contour():
    pic = cv2.imread(ori_file_path)
    pic_gray = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
    ret, binary_pic = cv2.threshold(pic_gray, 127, 255, cv2.THRESH_BINARY)
    contours,_ = cv2.findContours(binary_pic, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(pic, contours, -1, (0, 255, 0), 3)
    pic = cv2.resize(pic,(240, 320))
    # show_image("contour", pic)
    cv2.imwrite("contour.jpg",pic)

# 二值图像
def binary_img():
    pic_gray = cv2.imread(ori_file_path, 0)
    # pic_gray = cv2.resize(pic_gray,(127,170))
    ret,binary=cv2.threshold(pic_gray,127,255,cv2.THRESH_BINARY)
    # show_image("binary", binary)
    cv2.imwrite("binary.jpg",binary)

# 形态学操作
def opt_morphology():
    # 腐蚀
    pic = cv2.imread(ori_file_path, 0)
    kernel_er = np.ones((9,9), np.uint8)
    eroded = cv2.morphologyEx(pic, cv2.MORPH_ERODE, kernel_er)
    cv2.imwrite("er.jpg", eroded)
    # plt.subplot(141)
    # plt.imshow(eroded)

    # 膨胀
    kernel_ex = np.ones((9,9), np.uint8)
    extension = cv2.morphologyEx(pic, cv2.MORPH_DILATE, kernel_ex)
    # plt.subplot(142)
    # plt.imshow(extension)
    cv2.imwrite("ex.jpg", extension)

    # 开 腐蚀-膨胀
    open_pic = cv2.morphologyEx(pic, cv2.MORPH_ERODE, kernel_er)
    open_pic = cv2.morphologyEx(open_pic, cv2.MORPH_DILATE, kernel_ex)
    # plt.subplot(143)
    # plt.imshow(open_pic)
    cv2.imwrite("open.jpg", open_pic)

    # 闭 膨胀-腐蚀
    close_pic = cv2.morphologyEx(pic, cv2.MORPH_DILATE, kernel_ex)
    close_pic = cv2.morphologyEx(close_pic, cv2.MORPH_ERODE, kernel_er)
    # plt.subplot(144)
    # plt.imshow(close_pic)
    cv2.imwrite("close.jpg", close_pic)

    plt.show()

# canny检测边缘
def check_outline():
    pic = cv2.imread(ori_file_path)
    edged = cv2.Canny(pic, 30, 200)
    result_pic = cv2.resize(edged,(240,320))
    # show_image('canny', result_pic)
    cv2.imwrite("canny.jpg", result_pic)

# 颜色识别 找到原图中最多的颜色
def color_recognize():
    pic = cv2.imread(ori_file_path)

    ball_color = 'green'

    color_dist = {'red': {'Lower': np.array([0, 60, 60]), 'Upper': np.array([6, 255, 255])},
              'blue': {'Lower': np.array([100, 80, 46]), 'Upper': np.array([124, 255, 255])},
              'green': {'Lower': np.array([35, 43, 35]), 'Upper': np.array([90, 255, 255])},
              }
    
    gs_frame = cv2.GaussianBlur(pic, (5, 5), 0)
    hsv = cv2.cvtColor(gs_frame, cv2.COLOR_BGR2HSV)
    erode_hsv = cv2.erode(hsv, None, iterations=2)
    inRange_hsv = cv2.inRange(erode_hsv, color_dist[ball_color]['Lower'], color_dist[ball_color]['Upper'])
    cnts = cv2.findContours(inRange_hsv.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

    cv2.drawContours(pic, cnts, -1, (0, 255, 255), 2)

    # cv2.imshow('camera', pic)
    # cv2.waitKey(0)
    cv2.imwrite("col_rec.jpg", pic)

# 图片滤波
def pic_filter():
    pic = cv2.imread(ori_file_path)
    pic = cv2.resize(pic,(240,320))
    GaussianBlur=cv2.GaussianBlur(pic,(5,5),1)

    plt.subplot(211)
    plt.imshow(GaussianBlur)

    plt.subplot(212)
    plt.imshow(pic)

    plt.savefig("filter.jpg")


check_contour()
binary_img()
check_outline()
pic_filter()
opt_morphology()
color_recognize()