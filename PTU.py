####### WRITTEN TO CONTROL FLIR5 PAN AND TILT UNITS #######

####### MAINTAINER: DENIZ KARTAL ######

####### REFERENCE #######
# E-Series-Command-Reference-Manual.pdf -> https://flir.netx.net/file/asset/11554/original/attachment
# PTU-5-User-Manual.pdf -> https://flir.netx.net/file/asset/13941/original/attachment
# FLIR website -> https://www.flir.com/products/ptu-5/

####### IMPORTANT ############
# PTU cannot move to all possible positions or degrees(in angle), therefore, be careful
# when issuing a command to move the PTU. I suggest to read the documentation of the PTU 
# before issuing the movement commands.

from time import sleep
import serial
import socket

class PTU():
    # if you encounter a problem with serial communication
    # give permissions to the USB port by
    # sudo chmod 666 <path>
    # e.g. <path> -> /dev/ttyUSB0
    def __init__(self, serial_port = "/dev/ttyUSB0"):
        self.serial_port = serial_port
        # start a serial communication
        self.ser = serial.Serial(self.serial_port)
        print("Serial communication started over {}".format(self.serial_port))
        
        self.sock = None
        self.IP = None
        self.port = None
        
        self.step_mode = None
        self.resolution = None
        
        # command execution
        self.total_fail = 0
        self.execution_state = True
        self.first_failure = True

    # send serial commands
    def serial_send(self, command):
        self.ser.write(("{} ".format(command)).encode("utf-8"))
        sleep(0.02) # wait for 20ms for the PTU to respond
        received_decoded = None
        # wait while receiving
        while self.ser.inWaiting():
            received_encoded = self.ser.readline()
            received_decoded = received_encoded.decode("utf-8")
        return received_decoded
    
    # close the serial communication 
    def serial_close(self):
        self.ser.close()
        print("serial communication over {} has been closed".format(self.serial_port))
        self.serial_port = None
        self.ser = None
    
    # PTU responds with a success or failure code to the command it receives
    def success(self, r):
        return r if((r != None) and (r.find('*') != -1) and (r.find('!') == -1)) else None
    
    # get the IP address of the PTU by sending a command over serial
    def get_IP(self):
        r = self.serial_send("NI")
        if self.success(r) != None:
            start = r.find("IP: ") + len("IP: ")
            end = r.find("\r\n")
            return r[start: end]
        else:
            return None
    
    # serial communication is used to get the IP address of the PTU once
    # the IP address is gathered communication over a socket will start
    # since ethernet is faster
    def start_socket(self):
        print("Starting the socket..")
        if ((self.sock == None) and (self.IP == None) and (self.port == None)):
            IP = self.get_IP()
            if IP != None:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.port = 4000
                self.IP = IP
                self.sock.connect((self.IP, self.port))
                sleep(0.1)
                print("Socket has been started over {}:{}".format(self.IP, self.port))
                print(self.sock.recv(2048).decode("utf-8"))
            else:
                print("Serial respond from the PTU was very slow! Please configure the sleep-time after writing to the serial port.")
        else:
            print("Socket has been already started over 0{}:{}".format(self.IP, self.port))
    
    # close the socket
    def socket_close(self):
        self.sock.close()
        self.sock = None
    
    # send a command over the socket
    def socket_send(self, command):
        # send the command
        self.sock.send(("{} ".format(command)).encode("utf-8"))
        sleep(0.001)
        # get the respond from the PTU, PTU replies with a command
        received = self.sock.recv(2048).decode("utf-8")
        # return the received command if the command or the query sent was succesfully executed otherwise return None
        return self.success(received)
    
    # receive messages over the open socket
    def sock_receive(self):
        return self.sock.recv(2048).decode("utf-8")

    # most of the necessary commands are available on this file but
    # in case you want to execute a command on the PTU use this method
    # to send the command
    def execute_command(self, command):
        # send the command and receive PTU’s response to that command
        received = self.socket_send(command)
        # if the received is not none some action has happened
        if received != None:
            self.execution_state = True
            print(received)
        else:
            # if the response from the PTU is none
            # execution could not happen
            self.execution_state = False
            print("Command execution Failed!")
            
            if self.first_failure != self.execution_state:
                print("Execution Failed for the first time")
                print(self.sock.recv(2048).decode("utf-8"))
            else:
                print("Execution failed more than once")
        
            self.first_failure = self.execution_state

        print(self.execution_state)
        print(self.first_failure)

    # set the step mode
    def set_step_mode(self, step_mode):
        step_modes = {
            "half": ["WPH", "WTH", 0.02],
            "quarter": ["WPQ", "WTQ", 0.01],
            "eighth": ["WPE", "WTE", 0.005],
        }
        self.execute_command(step_modes.get(step_mode)[0])
        print("sleeping for 0.5 second")
        sleep(0.5)
        self.execute_command(step_modes.get(step_mode)[1])
        print("sleeping for 0.5 second")
        sleep(0.5)
        self.axis_reset(pan = True, tilt = True)
        self.resolution = step_modes.get(step_mode)[2]
    
    # reset axis
    def axis_reset(self, pan = False, tilt = False):
        if pan:
            self.socket_send("RP")
            print("sleeping for 2 seconds")
            sleep(2)
        if tilt:
            self.socket_send("RT")
            print("sleeping for 2 seconds")
            sleep(2)
        else:
            print("Please specify at least on axis, pan or tilt for axis reseting!")

    # move the PTU to the x direction coordinate, panning
    def move_x_to(self, position):
        # example respond: "PP100 *"
        command = "PP{}".format(position)
        self.execute_command(command)

    # move the PTU to the y direction coordinate, tilting
    def move_y_to(self, position):
        # example respond: "TP100 *"
        command = "TP{}".format(position)
        self.execute_command(command)

    # move the PTU by the number of positions specified in the x direction, panning
    # number of position move in each step can be set using set_step_mode function
    # get the number of positions in each step by num_of_positions function, resolution
    def move_x_by(self, num_of_positions):
        # example respond: "PO100 *"
        command = "PO{}".format(num_of_positions)
        self.execute_command(command)

    # move the PTU by the number of positions specified in the y direction, tilting
    # number of position move in each step can be set using set_step_mode function
    # get the number of positions in each step by num_of_positions function, resolution
    def move_y_by(self, num_of_positions):
        # example respond: "TO100 *"
        command = "TO{}".format(num_of_positions)
        self.execute_command(command)

    def num_of_positions(self, angle):
        return int(angle/self.resolution)
    
    # move the PTU to the x direction coordinate in degrees (0-360), panning
    def move_x_to_degrees(self, angle):
        position = self.num_of_positions(angle)
        self.move_x_to(str(position))
    
    # move the PTU to the y direction coordinate in degrees (0-360), tilting
    def move_y_to_degrees(self, angle):
        position = self.num_of_positions(angle)
        self.move_y_to(str(position))

    # move the PTU by degrees in angle in the x direction, panning
    def move_x_by_degrees(self, angle):
        num_of_positions = self.num_of_positions(angle)
        self.move_x_by(str(num_of_positions))
    
    # move the PTU by degrees in angle in the y direction, tilting
    def move_y_by_degrees(self, angle):
        num_of_positions = self.num_of_positions(angle)
        self.move_y_by(str(num_of_positions))
    
    # make the PTU to wait
    def ptu_await(self):
        # PTU waits to complete the previous position commands
        command = "A"
        self.execute_command(command)