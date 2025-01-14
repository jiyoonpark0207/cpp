#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point
import numpy as np
import math

import time

class MoveOdom (object):
    def __init__(self):
        # Target direction and distance in 2D referenced to CURRENT postition
        self.linear_speed = 0.01 #0.01 # 1 m/s
        self.direction = np.array([-1, 0]) # (0, -1) is moving left
        self.target_dist = 0.1 # in meter
        self.target_position = self.direction * self.target_dist

        # Create a global variable for publising a Twist ("cmd_vel") message
        self.move = Twist()
        self.reached = False

        # Get the inital position. This will be a reference point for calculating
        # the distance moved
        self.get_init_position()

        # Create a publisher that moves the robot
        self.move_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        # create a subscriber for getting new Odometry messages
        rospy.Subscriber('/vive_pose/filtered', Odometry, self.odom_callback)

    def get_init_position(self):
        data_odom = None
        # wait for a message from the odometry topic and store it in data_odom when available
        while data_odom is None:
            try:
                data_odom = rospy.wait_for_message('/vive_pose/filtered', Odometry, timeout=1)
                print("odom acheived")
                ### real robot working code
                # data_odom = rospy.wait_for_message("/ridgeback_velocity_controller/odom", Odometry, timeout=1)
            except:
                rospy.loginfo("Current odom not ready yet, retrying for setting up init pose")

        # Store the received odometry "position" variable in a Point instance
        self._current_position = Point()
        self._current_position.x = data_odom.pose.pose.position.x
        self._current_position.y = data_odom.pose.pose.position.y
        self._current_position.z = data_odom.pose.pose.position.z
        self.target_position += np.array([data_odom.pose.pose.position.x, data_odom.pose.pose.position.y])
        print(self._current_position)
        print(self.target_position)

    
    def odom_callback(self, msg):
        # get the distance moved from the message
        new_position = msg.pose.pose.position

        # If distance is less than the target, continue moving the robot
        # Otherwise, stop it (by pubishing `0`)
        dist = self.calculate_distance(self.target_position, new_position)
        print(dist)
        # if (iiwa_done):
        if dist > 0.001:
            self.move.linear.x = self.linear_speed * self.move_next[0]
            self.move.linear.y = self.linear_speed * self.move_next[1]

        if dist < 0.001:
            print("REACHED!!")
            self.move.linear.x = 0
            self.move.linear.y = 0
            self.reached = True
            # Get the inital position. This will be a reference point for calculating
            # the distance moved
            time.sleep(10)
        if not self.reached :
            self.move_pub.publish(self.move)

    def calculate_distance(self, target_position, new_position):
        """Calculate the distance between two Points (positions)."""
        x2 = new_position.x
        x1 = target_position[0]
        y2 = new_position.y
        y1 = target_position[1]
        dist = math.hypot(x2 - x1, y2 - y1)
        x = x1-x2
        y = y1-y2
        self.move_next = unit_vector([x,y])
        print(f'current pose: {x2, y2}\ntarget pose:{x1, y1} \nmove next: {self.move_next}')
        return dist
import numpy as np

def unit_vector(vector):
    vector=np.array(vector)
    unit_vector = vector / (vector**2).sum()**0.5
    return unit_vector

if __name__ == '__main__':
    # create a node for running the program
    rospy.init_node('move_odom_tf', anonymous=True)
    # create an instance of the MoveOdom
    odom_obj = MoveOdom()
    # Keep the program running
    rospy.spin()

