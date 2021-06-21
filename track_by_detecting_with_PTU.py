####### MAINTAINER: DENIZ KARTAL ######

##### IMPORTANT ######
# FEEL FREE TO PLAY AROUND WITH THE PID VARIABLES TO TUNE IT
# https://www.csimn.com/CSI_pages/PIDforDummies.html

##### REFERENCES ######
# PID CONTROLLER - https://pidexplained.com/pid-controller-explained/
import cv2
from argparse import ArgumentParser
from os import sys
from PTU import PTU
from Detector import Detector

# CHECK IF THE TRACKER IS VALID
# RETURN THE TRACKER NAME IF VALID
# OTHERWISE RETURN NONE

def main():
    parser = ArgumentParser()

    parser.add_argument("-v", "--video", required=True, help="video path, to find out the webcam path issue 'ls /dev/video*' command on the terminal", type=str)
    parser.add_argument("-o", "--object_detection_model", required=True, help='Path to the saved object detection model folder.', type=str)
    parser.add_argument("-l", "--labelmap", required=True, help="Path to the label map file (.pbtxt).")
    parser.add_argument("-s", "--serial", required=False, help="Serial port to communicate with the PTU. To find out issue 'ls /dev/tty*' command on the terminal")

    args = vars(parser.parse_args())

    detector = Detector(args["object_detection_model"], args["labelmap"], 0.5)

    # IF SERIAL PORT IS GIVEN, PTU WILL BE USED
    # OTHERWISE PTU IS NOT GONNA BE USED
    if args["serial"] != None:
        # PROPORTIONAL-INTEGRAL-DERIVATIVE VARIABLES
        # 
        # kP kI kD
        x_PID = [0.02, 0, 0]
        y_PID = [0.02, 0, 0]
        prev_error_x = 0
        prev_error_y = 0
        integral_x = 0
        integral_y = 0

        # CONFIGURE PTU
        ptu = PTU(args["serial"])
        # START THE COMMUNICATION OVER SOCKET
        ptu.start_socket()
        # NO NEED TO USE THE SERIAL ANYMORE SINCE, SOCKER HAS BEEN CREATED
        ptu.serial_close()
        # SET THE STEP MODE
        ptu.set_step_mode("eighth")
        # MOVE X AND Y TO 0, 0 COORDINATE
        ptu.move_x_to_degrees(0)
        ptu.move_y_to_degrees(0)
    else:
        print("You did not choose to activate the PTU!")
    
    # CONFIGURE THE DETECTOR
    detector = Detector(args["object_detection_model"], args["labelmap"], 0.5)

    # VIDEO CAPTURE VIA THE VIDEO PATH
    video_capture = cv2.VideoCapture(args["video"])

    # RUN CONTINOUSLY UNTIL USER PRESSES Q TO QUIT!
    while(True):
        ret, frame = video_capture.read()

        if ret is False:
            print("Could not read a frame over {}".format(args["video"]))
            break

        # HEIGHT AND WIDTH OF THE FRAME
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
            
            # IF SERIAL PORT IS PROVIDED
            # THAT MEANS PTU IS ACTIVATED
            # SO CONTROL THE PTU
            # TO BRING THE CENTER OF THE OBJECT TO THE
            # CENTER OF THE FRAME
            if args["serial"] != None:
                # distance(aka. error) between frame_center and object_center
                # ERROR IN THE X AXIS
                error_x = obj_center_x - frame_center_x
                # ERROR IN THE Y AXIS
                error_y = frame_center_y - obj_center_y

                print("Error in x: {}, in y: {}".format(error_x, error_y))

                # PID for x
                proportional_x = error_x
                integral_x = integral_x + error_x
                differential_x = abs(prev_error_x - error_x)
                u_x = round(x_PID[0] * proportional_x + x_PID[1] * integral_x + x_PID[2] * differential_x, 3)

                # PID for y
                proportional_y = error_y
                integral_y = integral_y + error_y
                differential_y = abs(prev_error_y - error_y)
                u_y = round(x_PID[0] * proportional_y + x_PID[1] * integral_y + x_PID[2] * differential_y, 3)

                prev_error_x = error_x
                prev_error_y = error_y

                print("u_x(t): {}, u_y(t): {}".format(u_x, u_y))
                
                # IGNORE SMALL ERRORS!
                if error_x**2 > 100:
                    ptu.move_x_by_degrees(u_x)
            
                if error_y**2 > 100:
                    ptu.move_y_by_degrees(-u_y)
        
        cv2.imshow("Frame", frame)

        # get the user input
        key = cv2.waitKey(1) & 0xFF
        
        # EXIT THE PROGRAM
        if(key == ord("q")):
            video_capture.release()
            cv2.destroyAllWindows()

            if args["serial"] != None:
                ptu.move_x_to(0)
                ptu.move_y_to(0)
                ptu.socket_close()

            sys.exit("Exiting the program.")

if __name__ == "__main__":
    main()