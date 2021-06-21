####### WRITTEN TO TEST THE OBJECT DETECTION MODEL WITH IMAGES #######

####### MAINTAINER: DENIZ KARTAL ######

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
import tensorflow as tf
from PIL import Image
import os
import sys
import glob
import numpy as np
import cv2
from argparse import ArgumentParser

def get_arr_with_detections(img_path, detect_fn, category_index):
    # LOAD THE IMAGE
    img = Image.open(img_path)

    # CONVERT IMAGE INTO NUMPY ARRAY
    img_arr = np.array(img)

    # CONVERT ARRAY INTO A TENSOR
    img_tensor = tf.convert_to_tensor(img_arr)

    # THE MODEL EXPECTS A BATCH(????) OF IMAGES
    img_tensor = img_tensor[tf.newaxis, ...]

    # GET OBJECTS DETECTED IN THAT IMAGE
    detections = detect_fn(img_tensor)
    
    # ALL OUTPUTS IN DETECTIONS ARE BATCHES
    # CONVERT THOSE INTO NUMPY ARRAYS
    # TAKE THE FIRST ELEMENT AND REMOVE THE REST(BATCHES)
    num_of_detections = int(detections.pop("num_detections"))
    detections = {key: value[0, :num_of_detections].numpy() for key, value in detections.items()}
    detections["num_detections"] = num_of_detections

    # DETECTION CLASSES, AKA LABELS SHOULD BE TYPE OF INTEGERS
    detections["detection_classes"] = detections["detection_classes"].astype(np.int64)
    print(list(detections.keys()))
    # CREATE A NUMPY ARRAY WITH DETECTED IMAGES
    img_arr_with_detections = img_arr.copy()

    viz_utils.visualize_boxes_and_labels_on_image_array(
        img_arr_with_detections,
        detections['detection_boxes'],
        detections['detection_classes'],
        detections['detection_scores'],
        category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=200,
        min_score_thresh=.30,
        agnostic_mode=False)
    
    print(img_arr_with_detections)
    return img_arr_with_detections

def main():
    parser = ArgumentParser()

    parser.add_argument("-s", "--savedmodel", required=True, help="Path to the saved model folder.")
    parser.add_argument("-l", "--labelmap", required=True, help="Path to the label map file (.pbtxt).")
    parser.add_argument("-i", "--images", required=True, help="Path to the images folder.")

    args = vars(parser.parse_args())
    # CHECK IF THE PATHS EXIST
    for key in args:
        if not os.path.exists(args[key]):
            sys.exit("{} does not exist. Exiting the program!".format(args[key]))

    # LOAD SAVED MODEL AND BUILD THE DETECTION FUNCTION
    detect_fn = tf.saved_model.load(args["savedmodel"])

    # LOAD LABEL MAP DATA FOR PLOTTING
    # LABEL MAP INDEX NUMBERS CORRESPONDS TO CLASS NAMES
    category_index = label_map_util.create_category_index_from_labelmap(args["labelmap"], use_display_name=True)
    
    # GET ALL THE IMAGE FILES FROM THE IMAGES DIRECTORY
    img_files = glob.glob(args["images"] + "/*.jpg")

    # GO THROUGH ALL THE IMAGES AND GET IMAGE ARRAYS FOR EACH IMAGE WITH THE DETECTED OBJECTS IN THAT IMAGE
    img_arrays_with_detections = [get_arr_with_detections(img_file_path, detect_fn, category_index) for img_file_path in img_files]

    # PLOT ALL THE IMAGES
    print("Plotting images")
    for img_arr_with_detections in img_arrays_with_detections:
        cv2.imshow("Frame", img_arr_with_detections)
        print("Plotting an image!")
        # WAIT UNTIL USER TO PRESS A KEY, THEN GO TO THE NEXT IMAGE
        print("Press any key on your keyboard to go to the next image!")
        cv2.waitKey()

    print("Destroying windows!")
    cv2.destroyAllWindows() # destroys the window showing image
    sys.exit("Exiting the program!")

if __name__ == "__main__":
    main()