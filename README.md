# Tracking drones with a PTU(Pan and Tilt Unit)

## Setup
- After cloning the repo issue "pip install -r requirements.txt" to install the packages.
- issue "protoc --version" on the terminal to check if you have protoc installed. 
- If not install protocol buffer https://grpc.io/docs/protoc-installation/
- run the following commands on the terminal for TensorFlow Object Detection API
<pre>
cd models/research/
protoc object_detection/protos/*.proto --python_out=.
cp object_detection/packages/tf2/setup.py .
python3 -m pip install .
</pre>

## Folder structure
- FLIR-5-PAN-AND-TILT-UNIT/ contains the documentation from FLIR.
- images/ contains some test images for drone detection.
- models/ contains the TensorFlow Object Detection API.
- pretrained-models/ contains all the pretrained models. If you train your own model, please put your exported model under this directory!

## Usage
### Testing the object detection model with a webcam.
<pre>
detect_webcam.py -v [video_path] -s [saved_model] -l [label_map_file]
[video_path] - Path to the webcam, e.g /dev/video0
[saved_model_folder] - Path to the object detection model. This folder contains /variables/ /assets/ saved_model.pb
[label_map_file] - Path to the label map file (.pbtxt) which corresponds to the saved model.
</pre>

### Testing the object detection model with images.
<pre>
detect_image.py -s [saved_model] -l [label_map_file] -i [images_path] 
[images_path] - Path to the images folder.
[saved_model_folder] - Path to the object detection model. This folder contains /variables/ /assets/ saved_model.pb
[label_map_file] - Path to the label map file (.pbtxt) which corresponds to the saved model.
</pre>

### Tracking the objects using the object detection model with a PTU
- First object Detection model is provided to the program.
- Then the system uses the model to detect objects on each frame.(It is expected that only a single object, such as a drone, should be present on the scene of the camera)
- Host machine communicates with the Pan and Tilt Unit to take the center of the object that is being tracked into center of the frame.
- PID model is used to balance the movements of the PTU so that it does not move from a point to point very quicky, but instead the movements are smooth.
- Communication between with the PTU happens over ethernet, at first the IP address of the PTU is gathered using the serial communication.
- Note that PTU should be connected to the same network as the controller(laptop, embedded board etc.) for communication to happen.
- Please read the documentations before using the PTU. Documentations can be found under /FLIR-5-PAN-AND-TILT-UNIT/.

<pre>
track_by_detecting_with_PTU.py -v [video_path] -o [object_detection_model] -l [label_map_file] -s [serial] 

[video_path] - Path to the webcam, e.g /dev/video0
[object_detection_model] - Path to the object detection model. This folder contains /variables/ /assets/ saved_model.pb
[label_map_file] - Path to the label map file (.pbtxt) which corresponds to the saved model.
[serial] - Path to the serial port, to start the communication with the PTU.
</pre>

### Tracking the objects using a tracking algorithm with a PTU
- A tracking algortihm is inputted to the program.
- First a bounding box around the object, that is supposed to be tracked, is selected. Then chosen Object Tracking Algorithm updates the bounding box for each frame.
- The following steps are same as in tracking by detection.
<pre>
track_by_tracking_with_PTU.py -v [video_path] -t[tracker] -s [serial] 

[video_path] - Path to the webcam, e.g /dev/video0
[tracker] - Object Tracking algoritm. ["kcf", "csrt", "mil"].
[serial] - Path to the serial port, to start the communication with the PTU.
</pre>
