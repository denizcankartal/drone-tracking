####### MAINTAINER: DENIZ KARTAL ######

# TRACK AN OBJECT BY USING THE TRACKING ALGORITHMS FROM OPENCV

# WHEN CREATING A TRACKER IF YOU ENCOUNTER A PROBLEM SUCH AS THE FOLLOWING:
# AttributeError: module 'cv2.cv2' has no attribute 'Tracker_create'
# YOU MUST UNINSTALL YOUR OPENCV AND INSTALL OPENCV 3.4+


import cv2

class Tracker:
    def __init__(self, tracker_name):
        # tracker_name = ["kcf", "csrt", "mil"]
        self.tracker_name = tracker_name
        # bounding box to be tracked
        self.bounding_box = None
        # center of the object
        self.object_center = None
        self.lost = None
    
    def initialize_tracker(self):
        # available trackers from opencv
        object_trackers = {
            "csrt": cv2.TrackerCSRT_create,
		    "kcf": cv2.TrackerKCF_create,
		    "mil": cv2.TrackerMIL_create,
        }
        # set the tracker
        self.tracker = object_trackers[self.tracker_name]()
    
    # initial_bounding_box: bounding box defined/selected by
    # the user when starting the tracker to track
    # frame: current frame
    def start_tracker(self, initial_bounding_box, frame):
        self.lost = False
        self.tracker.init(frame, initial_bounding_box)
        print("{} tracker is started".format(self.tracker_name))
    
    # update the bouding box for each frame
    def update_bounding_box(self, frame):
        success, bounding_box = self.tracker.update(frame)
        # tracker may loose the object if success is not
        # True that means the tracker has lost the object
        # on that frame

        if success:
            self.bounding_box = bounding_box
            self.lost = False
        elif not success:
            self.lost = True
            print("Object is lost!")
        else:
            print("Something unexpected occured while updating the bounding box of the object that is being tracked!!!")
    
    # update the center of the object that is being tracked
    # on that current frame
    def update_object_center(self):
        try:
            # bounding_box is a list of coordinate points
            # contains x coordinate, y coordinate, width, and height
            x, y, w, h = [int(a) for a in self.bounding_box]

            # calculate object center on the x axis
            object_center_x = int(x + (w / 2.0))

            # calculate object center on the y axis
            object_center_y = int(y + (h / 2.0))

            # update the center of the object
            self.object_center = [object_center_x, object_center_y]
        except:
            print("Failed to update the center of the object!")
            self.bounding_box_available = False
    
    def get_last_object_center(self):
        return self.object_center

    def get_last_bounding_box(self):
        return self.bounding_box