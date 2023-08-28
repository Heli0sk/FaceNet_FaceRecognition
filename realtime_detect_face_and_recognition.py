import tensorflow as tf
from collect_frame_to_csv import collect_frame_to_csv
import detect_face
import cv2
from cal_128XVector_user_facenet import cal_128_vector,build_facenet_model,cal_dist_from_csv

def realtime_detect(csv_dir= './data/data.csv'):
    # csv_dir = './data/data.csv'#人脸128向量的数据
    # 调用facenet模型
    sess1, images_placeholder, phase_train_placeholder, embeddings = build_facenet_model()
    image_size = 200
    minsize = 20
    threshold = [0.6, 0.7, 0.7]
    factor = 0.709  # scale factor
    # print("Creating MTcnn networks and load paramenters..")

    #########################build mtcnn########################
    with tf.Graph().as_default():
        sess = tf.Session()
        with sess.as_default():
            pnet, rnet, onet = detect_face.create_mtcnn(sess, './model/')

    capture = cv2.VideoCapture(0)
    while (capture.isOpened()):
        ret, frame = capture.read()
        bounding_box, _ = detect_face.detect_face(frame, minsize, pnet, rnet, onet, threshold, factor)

        nb_faces = bounding_box.shape[0]  # 人脸检测的个数
        # 标记人脸
        for face_position in bounding_box:
            rect = face_position.astype(int)
            image=frame[rect[1]:rect[3],rect[0]:rect[2]]#截取人脸的ROI区域
            array=cal_128_vector(image,sess1, images_placeholder, phase_train_placeholder, embeddings)#计算人脸的128向量
            dist,label=cal_dist_from_csv(csv_dir,array) # 返回最小距离和人脸所属标签
            # 识别到人怎么输出？
            # label是得到的标签

            # 矩形框
            cv2.rectangle(frame, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 255), 2, 1)
            cv2.putText(frame, "faces:%d" % (nb_faces), (10, 20), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 4)
            cv2.putText(frame, '%.2f' % (dist), (rect[0], rect[1] - 30), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 4)
            cv2.putText(frame, label, (rect[0], rect[1] ), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 4)

        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xff == 27: #ESC键退出
            break
    capture.release()
    cv2.destroyAllWindows()

if __name__=="__main__":
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    with tf.Session(config=config) as session:  # 解决GPU缓存不足问题
        # collect_frame_to_csv()
        realtime_detect()
