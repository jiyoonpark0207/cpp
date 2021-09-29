#! /usr/bin/env python3
from sensor_msgs.msg import LaserScan
import rospy

from tools import tools_etc
from tools import tools_cmd_vel

angle_90 = 0

# laser scanner


def callback_laser(msg):
    global angle_90

    angle_90 = tools_etc.average(msg.ranges, 90)
    # print(angle_90)


def keep_distance(distance):
    sub = rospy.Subscriber('/front/scan', LaserScan, callback_laser)

    speed = 0.05
    duration = 0.05

    thresh = 0.05
    rospy.sleep(1)

    while True:
        if angle_90 - distance > thresh:  # 1.3m - 1m  = 0.3 m > 0.1
            print(angle_90, end=": ")
            tools_cmd_vel.move_forward(speed, duration)
        elif angle_90 - distance < -thresh:  # 0.7m - 1m  = -0.3 m < -0.1
            print(angle_90, end=": ")
            tools_cmd_vel.move_backward(speed, duration)
        else:
            print("distance to cylinder :", angle_90)
            print("done")
            break


if __name__ == "__main__":

    rospy.init_node('cylinder_laser_right')

    keep_distance(1.0)
    # rospy.spin()