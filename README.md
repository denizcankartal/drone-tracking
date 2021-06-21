# Tracking drones with a PTU(Pan and Tilt Unit)

### Components

Component | Brand, Type | Documentation | Role |
 :------------: | :-----------: | :-----------: | ----------- |
Pan and Tilt Unit | __[FLIR PTU-5](https://www.flir.com/products/ptu-5/)__ |Go to FLIR-5-PAN-AND-TILT-UNIT/ under this repo| Keep the tracked object in the center of the frame. |
Embedded Computing Board | __[Nvidia Jetson NX](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-xavier-nx/)__ | __[Getting Started](https://developer.nvidia.com/embedded/learn/get-started-jetson-xavier-nx-devkit)__ <br> __[Nvidia Jetson Forums](https://forums.developer.nvidia.com/c/agx-autonomous-machines/jetson-embedded-systems/70)__| Object detection, object tracking, interface to the camera, and communication with the laser and the PTU.|
Laser Ranger| __[Bosch GLM 50c](https://www.bosch-professional.com/ao/en/products/glm-50-c-0601072C00)__ | __[Instruction Manual](https://www.bosch-professional.com/manuals/professional/ao/en/online-manual/200356428/en-AO/index.html)__ | Calculate the distance between the object and the system.|



## Approach
1. Start a communication between the host machine and the PTU over ethernet.
2. Use a detection model or a tracking algorithm to get a bounding box of the object on each frame.
3. Calculate the center of the object and the center of the frame for on the current frame.
4. Calculate the error, that is the distance between the center of the frame and object.
5. Use the PID controller to avoid the error.
6. Move the PTU to take the center of the object on to the center of that frame.
7. If the error is very low, communicate with the laser over Bluetooth to hit the target to find the range.
8. Go to step 2 and do the same for the next frame.

*Note that step-7 is not implemented yet!*

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

## Useful Resources for advancing this repo

[TensorFlow Object Detection API](https://github.com/tensorflow/models/tree/master/research/object_detection)

[TensorFlow Model Garden](https://github.com/tensorflow/models)

[TensorFlow 2 Detection Model Zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf2_detection_zoo.md)

[Object Detection From TF2 Saved Model](https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/auto_examples/plot_object_detection_saved_model.html)

[Object Detection From TF2 Checkpoint](https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/auto_examples/plot_object_detection_checkpoint.html)

[Detect Objects Using Your Webcam](https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/auto_examples/object_detection_camera.html)

[PySerial](https://pyserial.readthedocs.io/en/latest/pyserial.html)

[FLIR PTU-5](https://www.flir.com/products/ptu-5/)

[OpenCV](https://docs.opencv.org/master/d6/d00/tutorial_py_root.html)

[Multiple Object Tracking Algorithms](https://manivannan-ai.medium.com/multiple-object-tracking-algorithms-a01973272e52)

[Multiple Object Tracking in Realtime](https://opencv.org/multiple-object-tracking-in-realtime/)

[Object Tracking using OpenCV](https://learnopencv.com/object-tracking-using-opencv-cpp-python/)

[Quick Guide to Object Tracking](https://cv-tricks.com/object-tracking/quick-guide-mdnet-goturn-rolo/)

[Getting Started with Nvidia Jetson Xavier NX](https://developer.nvidia.com/embedded/learn/get-started-jetson-xavier-nx-devkit)

[jetson-inference from dusty-nv](https://github.com/dusty-nv/jetson-inference)

[BOSCH GLM rangefinder python repo from philipptrenz](https://github.com/philipptrenz/BOSCH-GLM-rangefinder)

[How to connect Bluetooth in Python to BOSCH GLM 50C](https://medium.com/analytics-vidhya/how-to-use-connect-bluetooth-in-python-from-scartch-to-bosch-glm-50-c-in-window-e75d8206fab4)

[PID controller explained](https://pidexplained.com/pid-controller-explained/)

[PID Tuning tutorial](https://www.neles.com/valves-services/pid-tuning-and-process-control-services/pid-tuning-tutorial/)
