####### MAINTAINER: DENIZ KARTAL ######

##### IMPORTANT ######
# FEEL FREE TO PLAY AROUND WITH THE PID VARIABLES TO TUNE IT
# https://www.csimn.com/CSI_pages/PIDforDummies.html

##### REFERENCES ######
# PID CONTROLLER - https://pidexplained.com/pid-controller-explained/
import cv2
from argparse import ArgumentParser
from os import sys
from Tracker import Tracker
from PTU import PTU

# CHECK IF THE TRACKER IS VALID
# RETURN THE TRACKER NAME IF VALID
# OTHERWISE RETURN NONE
def valid_tracker(tracker_name):
    tracker_names = ["csrt","kcf","mil"]

    if tracker_name in tracker_names:
        return tracker_name
    else:
        print("{} tracker is not avaiable! Please use of those: ")
        for idx, tracker in enumerate(tracker_names):
            print("{}. {}".format(idx, tracker))
        return None

def main():
    parser = ArgumentParser()

    parser.add_argument("-v", "--video", required=True, help="video path, to find out the webcam path issue 'ls /dev/video*' command on the terminal", type=str)
    parser.add_argument("-t", "--tracker", required=True, help='Tracker algorithm. Available tracking algorithms: ["csrt","kcf","mil"]', type=str)
    parser.add_argument("-s", "--serial", required=False, help="Serial port to communicate with the PTU. To find out issue 'ls /dev/tty*' command on the terminal", type=str)

    args = vars(parser.parse_args())
    
    tracker = None
    initial_bounding_box = None

    # CHECK IF THE TRACKER IS VALID
    tracker_name = valid_tracker(args["tracker"])
    if tracker_name is None:
        sys.exit("Exiting the program.")
    
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
    
    # CONFIGURE THE TRACKER
    tracker = Tracker(tracker_name)
    tracker.initialize_tracker()

    # VIDEO CAPTURE VIA THE VIDEO PATH
    video_capture = cv2.VideoCapture(args["video"])

    # RUN CONTINOUSLY UNTIL USER PRESSES Q TO QUIT!
    while(True):
        ret, frame = video_capture.read()

        # HEIGHT AND WIDTH OF THE FRAME
        (H, W) = frame.shape[:2]

        if ret is False:
            print("Could not read a frame over {}".format(args["video"]))
            break

        # IF BOUNDING BOX IS DEFINED
        # THAT MEANS THE USER STARTED AND FED THE TRACKER
        # WITH AN INITIAL BOUNDING BOX
        if (initial_bounding_box is not None):
            # update bounding box object [x, y, w, h] by updating the tracker
            # for the current frame
            tracker.update_bounding_box(frame)

            # update the center of the bounding box location 
            # on the current frame
            tracker.update_object_center()

            # CREATE A RED CIRCLE ON THE CENTER OF THE CURRENT FRAME
            frame_center_x = W // 2
            frame_center_y = H // 2
            cv2.circle(frame, (frame_center_x, frame_center_y), 3, (0,0,255), 3)

            last_oc = tracker.get_last_object_center()
            last_bb = tracker.get_last_bounding_box()

            # CHECK IF THE OBJECT IS LOST
            if tracker.lost:
                print("object is lost - last center: {}, {} - last bounding box(x, y, w, h): {}, {}, {}, {}".format(last_oc[0], last_oc[1], last_bb[0], last_bb[1], last_bb[2], last_bb[3]))
            if (not tracker.lost) and (len(last_oc) > 0) and (len(last_bb) > 0):
                print("tracking the object - current center: {}, {} - current bounding box(x, y, w, h): {}, {}, {}, {}".format(last_oc[0], last_oc[1], last_bb[0], last_bb[1], last_bb[2], last_bb[3]))

                # CREATE A GREEN CIRCLE ON THE CENTER OF THE OBJECT
                cv2.circle(frame, (last_oc[0], last_oc[1]), 3, (0, 255, 0), 3)

                # CREATE A GREEN RECTANGLE AROUND THE OBJECT
                cv2.rectangle(frame, (last_bb[0], last_bb[1]), (last_bb[0] + last_bb[2], last_bb[1] + last_bb[3]), (0, 255, 0), 2)
            
            # IF SERIAL PORT IS PROVIDED
            # THAT MEANS PTU IS ACTIVATED
            # SO CONTROL THE PTU
            # TO BRING THE CENTER OF THE OBJECT TO THE
            # CENTER OF THE FRAME
            if args["serial"] != None:
                # distance(aka. error) between frame_center and object_center
                # ERROR IN THE X AXIS
                error_x = last_oc[0] - frame_center_x
                # ERROR IN THE Y AXIS
                error_y = frame_center_y - last_oc[1]

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

        # START AND FEED THE OBJECT TRACKER WITH A BOUNDING BOX
        if(key == ord("s")):
            print("initializing a bounding box")
            # draw a bounding box then press enter
            # initial_bounding_box = (x_start, y_start, width, height)
            initial_bounding_box = cv2.selectROI("Frame", frame, fromCenter = False, showCrosshair = True)
            tracker.start_tracker(initial_bounding_box, frame)
        
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