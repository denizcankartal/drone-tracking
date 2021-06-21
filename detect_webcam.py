####### WRITTEN TO TEST THE OBJECT DETECTION MODELS WITH WEBCAM #######

####### MAINTAINER: DENIZ KARTAL ######

from Detector import Detector
import cv2
import os
from argparse import ArgumentParser
import sys

def main():
    parser = ArgumentParser()
    parser.add_argument("-v", "--video", required=True, help="video path, to find out the webcam path issue 'ls /dev/video*' command on the terminal", type=str)
    parser.add_argument("-s", "--savedmodel", required=True, help="Path to the saved model folder.")
    parser.add_argument("-l", "--labelmap", required=True, help="Path to the label map file (.pbtxt).")

    args = vars(parser.parse_args())

    # CHECK IF THE PATHS EXIST
    for key in args:
        if not os.path.exists(args[key]):
            sys.exit("{} does not exist. Exiting the program!".format(args[key]))

    detector = Detector(args["savedmodel"], args["labelmap"], 0.5)

    # VIDEO CAPTURE VIA THE VIDEO PATH
    video_capture = cv2.VideoCapture(args["video"])

    # RUN CONTINOUSLY UNTIL USER PRESSES Q TO QUIT!
    while(True):
        # READ CURRENT FRAME
        ret, frame = video_capture.read()

        if ret is False:
            print("Could not read a frame over {}".format(args["video"]))
            break
        
        (H, W) = frame.shape[:2]
        
        # CREATE A RED CIRCLE ON THE CENTER OF THE FRAME
        frame_center_x = W // 2
        frame_center_y = H // 2
        print("frame-center-x: {}, frame-center-y: {}".format(frame_center_x, frame_center_y))
        cv2.circle(frame, (frame_center_x, frame_center_y), 3, (0,0,255), 3)

        detector.get_detections(frame)
        
        if(detector.object_detected):
            print("An object detected!")

            # Go through all the detected objects!
            for bounding_box, detections_score, detection_classes_name in zip(detector.detections["bounding_box"], detector.detections["detection_scores"], detector.detections["detection_classes_names"]):
                ymin, xmin, ymax, xmax = bounding_box
                print("{} -> ymin: {}, xmin: {}, ymax: {}, xmax: {}".format(detection_classes_name, ymin, xmin, ymax, xmax))
                obj_center_x = int((xmax + xmin) // 2.0)
                obj_center_y = int((ymax + ymin) // 2.0)

                # GREEN CIRCLE ON THE OBJECT
                print("{} -> obj_center_x: {}, obj_center_y: {}".format(detection_classes_name, obj_center_x, obj_center_y))
                cv2.circle(frame, (obj_center_x, obj_center_y), 3, (0, 255, 0), 3)

                # GREEN RECTANGLE ON THE OBJECT
                cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255,0), 2)
                cv2.putText(frame, (detection_classes_name +"  "+ str(detections_score)), (int(xmin), int(ymin)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255, 0), 2)

        # SHOW THE FRAME
        cv2.imshow("Frame" ,frame)

        # GET USER INPUT
        key = cv2.waitKey(1) & 0xFF

        # EXIT THE PROGRAM
        if(key == ord("q")):
            video_capture.release()
            cv2.destroyAllWindows()

            sys.exit("Exiting the program!")

if __name__ == "__main__":
    main()