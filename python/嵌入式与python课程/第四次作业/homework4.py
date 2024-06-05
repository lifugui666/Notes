import cv2
import time
import threading



# 读取和保存图片
def read_and_save_pic():
    img = cv2.imread("./read_test.png")
    resized_img = cv2.resize(img,(100,200), interpolation=cv2.INTER_AREA)
    cv2.imwrite("./resized_read_test.png", resized_img)


# 录像 保存视频 在视频的左上角添加时间 yy/mm/dd/hh/mm/ss
def record_and_save():
    # pass
    # generate time stamp as file name 
    current_time = time.strftime('%Y%m%d%H%M%S', time.localtime())
    video_path = current_time + ".mp4"
    print("output file name:{}".format(video_path))
    # init cap 
    FPS = 24
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    wid = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    hig = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("shape of video {} * {}".format(wid, hig))
    vid_out = cv2.VideoWriter(video_path, fourcc, FPS, (wid, hig) )

    while(cap.isOpened):
        ret, frame = cap.read()
        # if ret:
        font = cv2.FONT_HERSHEY_SIMPLEX
        current_time = time.strftime('%Y%m%d%H%M%S', time.localtime())
        frame = cv2.putText(frame, current_time, (10,50), font, 1, (255,255,255), 2, cv2.LINE_AA)
        vid_out.write(frame)
        cv2.imshow("frame",frame)

        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    vid_out.release()
    cv2.destroyAllWindows()



# 打开录制的视频，回放，按s保存当前画面，保存为 时间码.png 按q退出
def playback_save_pic():
    video_path = "./20240411152831.mp4"
    cap = cv2.VideoCapture(video_path)
    while(cap.isOpened):
        ret, frame = cap.read()
        
        cv2.imshow("frame", frame)

        if cv2.waitKey(1) == ord('s'):
            current_time = time.strftime('%Y%m%d%H%M%S', time.localtime())
            img_path = current_time + ".png"
            cv2.imwrite(img_path, frame)

    cap.release()
    cv2.destroyAllWindows()
        




## 经测试可用
# read_and_save_pic()
# record_and_save()
# playback_save_pic()