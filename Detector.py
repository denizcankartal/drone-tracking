from object_detection.utils import label_map_util
import tensorflow as tf
import numpy as np
import cv2

class Detector:
    def __init__(self, saved_model_path, label_map_path, min_score):
        self.saved_model_path = saved_model_path
        self.label_map_path = label_map_path
        self.min_score = min_score

        # LOAD SAVED MODEL AND BUILD THE DETECTION FUNCTION
        print("Loading the saved model, and building a detection function.")
        self.detect_fn = tf.saved_model.load(self.saved_model_path)

        # LOAD LABEL MAP DATA FOR PLOTTING
        # LABEL MAP INDEX NUMBERS CORRESPONDS TO CLASS NAMES
        self.category_index = label_map_util.create_category_index_from_labelmap(self.label_map_path, use_display_name=True)

        self.object_detected = False
        self.detections = {}

        self.detections["detection_classes"] = None
        self.detections["raw_detection_scores"] = None
        self.detections["detection_boxes"] = None
        self.detections["detection_multiclass_scores"] = None
        self.detections["raw_detection_boxes"] = None
        self.detections["detection_anchor_indices"] = None
        self.detections["detection_scores"] = None
            
        # bounding box: ymin, xmin, ymax, xmax
        self.detections["bounding_box"] = None

        # CONVERT INDICES INTO CLASS NAMES
        self.detections["detection_classes_names"] = None

        # CONVERT FROM BGR TO RGB
        self.RGB_arr = None
    
    def get_detections(self, frame):
        frame_arr = np.expand_dims(frame, axis=0)

        # CONVERT ARRAY INTO A TENSOR
        #frame_tensor = tf.convert_to_tensor(frame_arr, dtype = tf.float32)
        frame_tensor = tf.convert_to_tensor(frame_arr)
        # THE MODEL EXPECTS A BATCH(????)
        #frame_tensor = frame_tensor[tf.newaxis, ...]

        # GET OBJECTS DETECTED IN THAT FRAME
        detections = self.detect_fn(frame_tensor)

        # ALL OUTPUTS IN DETECTIONS ARE BATCHES
        # CONVERT THOSE INTO NUMPY ARRAYS
        # TAKE THE FIRST ELEMENT AND REMOVE THE REST(BATCHES)
        num_of_detections = int(detections.pop("num_detections"))
        detections = {key: value[0, :num_of_detections].numpy() for key, value in detections.items()}
        detections["num_detections"] = num_of_detections

        # ONLY HIGH SCORED OBJECTS SHOULD STAY IN THE ARRAY
        new_arr = detections["detection_scores"] > self.min_score
        print(new_arr)
        if True in new_arr:
            self.object_detected = True
            # Select elements with True at corresponding value in bool array
            keys = [
                "detection_boxes",
                "detection_classes",
                "detection_anchor_indices",
                "raw_detection_scores",
                "detection_scores",
                "raw_detection_boxes",
                "detection_multiclass_scores",
            ]
            for key in keys:
                self.detections[key] = detections[key][new_arr]    
                
            # GET FRAME WIDTH AND HEIGHT
            (H, W) = frame.shape[:2]
            
            # bounding box: ymin, xmin, ymax, xmax
            self.detections["bounding_box"] = detections["detection_boxes"] * [H, W, H, W]

            # CONVERT INDICES INTO CLASS NAMES
            self.detections["detection_classes_names"] = np.array([self.category_index[int(class_idx)]["name"] for class_idx in detections["detection_classes"]])

            # CONVERT FROM BGR TO RGB
            self.RGB_arr = cv2.cvtColor(frame_arr, cv2.COLOR_BGR2RGB)
        else:
            print("object is lost!")
            self.object_detected = False