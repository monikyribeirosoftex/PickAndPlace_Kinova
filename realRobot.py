#! /usr/bin/env python3

###
# KINOVA (R) KORTEX (TM)
#
# Copyright (c) 2018 Kinova inc. All rights reserved.
#
# This software may be modified and distributed
# under the terms of the BSD 3-Clause license.
#
# Refer to the LICENSE file for details.
#
###

import sys
import os
import time
import threading
import keyboard
from kortex_api.autogen.messages import Base_pb2
from abstractRobot import AbstractRobot
from robotConnection import RobotConnection




# Maximum allowed waiting time during actions (in seconds)
TIMEOUT_DURATION = 60


class RealRobot(AbstractRobot):

    def __init__(self):
        """
        Method to initialize the robot class generate the necessary parameters for the operation
        """
        self.device_config = None
        self.gripper = None
        self.base_cyclic = None
        self.base = None
        self.action = None
        self.device = None
        self.active_state = None
        self.error_number = 0
        self.gripper_command = None
        self.arm_state_notif_handle = None
        self.critical_error = False
        self.action_finished = True
        self.final_position = None
        self.trajectory_info = []

    def move_to_home(self): 
            self.base_servo_mode = Base_pb2.ServoingModeInformation()
            self.base_servo_mode.servoing_mode = Base_pb2.SINGLE_LEVEL_SERVOING
            self.base.SetServoingMode(self.base_servo_mode)

            # Move arm to ready position
            action_type = Base_pb2.RequestedActionType()
            action_type.action_type = Base_pb2.REACH_JOINT_ANGLES
            action_list = self.base.ReadAllActions(action_type)
            action_handle = None
            for action in action_list.action_list:
                if action.name == "Home":
                    action_handle = action.handle

            if action_handle is None:
                print("Can't reach safe position. Exiting")
                return False

            e = threading.Event()
            notification_handle = self.base.OnNotificationActionTopic(
                self.check_for_end_or_abort(e),
                Base_pb2.NotificationOptions()
            )

            self.base.ExecuteActionFromReference(action_handle)
            finished = e.wait(TIMEOUT_DURATION)
            self.base.Unsubscribe(notification_handle)

            if finished:
                print("Safe position reached")
            else:
                print("Timeout on action notification wait")
            return finished

    def connect(self, connection_ip: str = "192.168.2.10"):
        self.device = RobotConnection.createTcpConnection(connection_ip)
        self.device.connect()
        self.request_devices_services()

    def request_devices_services(self) -> None:
        """
        Creates a connection to request services from the following devices:
        Base, BaseCyclic, Gripper, DeviceConfig

        Returns:
            None
        """
        self.base = self.device.get_base_client()
        self.base_cyclic = self.device.get_base_cyclic_client()
        self.gripper = self.device.get_gripper_cyclic_client()
        self.device_config = self.device.get_device_config_client()

    def disconnect(self):
        if self.device is None:
            return
        self.device.disconnect()
    

    def move_cartesian(self, pose_list: list[float]):
        # Starting Cartesian action movement
        action = Base_pb2.Action()
        action.name = "Example Cartesian action movement"
        action.application_data = ""

        cartesian_pose = action.reach_pose.target_pose
        cartesian_pose.x = pose_list[0]  # (meters)
        cartesian_pose.y = pose_list[1]  # (meters)
        cartesian_pose.z = pose_list[2]  # (meters)
        cartesian_pose.theta_x = pose_list[3]  # (degrees)
        cartesian_pose.theta_y = pose_list[4]  # (degrees)
        cartesian_pose.theta_z = pose_list[5]  # (degrees)

        e = threading.Event()
        notification_handle = self.base.OnNotificationActionTopic(
            self.check_for_end_or_abort(e),
            Base_pb2.NotificationOptions()
        )

        # Executing action
        self.base.ExecuteAction(action)

        # Waiting for movement to finish
        finished = e.wait(TIMEOUT_DURATION)
        self.base.Unsubscribe(notification_handle)

        if finished:
            pass
        else:
            print("Timeout on action notification wait")
        return finished

    def move_joints(self, joints_list: list[float]):
        # Starting angular action movement
        action = Base_pb2.Action()
        action.name = "Angular action movement"
        action.application_data = ""

        # Place arm straight up
        joint_id = 1
        for joint_value in joints_list:
            joint_angle = action.reach_joint_angles.joint_angles.joint_angles.add()
            joint_angle.joint_identifier = joint_id
            joint_angle.value = joint_value
            joint_id += 1

        e = threading.Event()
        notification_handle = self.base.OnNotificationActionTopic(
            self.check_for_end_or_abort(e),
            Base_pb2.NotificationOptions()
        )

        # Executing action
        self.base.ExecuteAction(action)

        # Waiting for movement to finish
        finished = e.wait(TIMEOUT_DURATION)
        self.base.Unsubscribe(notification_handle)

        if finished:
            pass
        else:
            print("Timeout on action notification wait")
        return finished
    
    def apply_emergency_stop(self):
        self.thread_on = True
        continue_ = True
        while continue_ and self.thread_on:
            if keyboard.is_pressed('space'):
                self.connect.apply_emergency_stop()
                print('Emergency stop activated')
                continue_ = False

    def clear_faults(self):
         """
        This method clears any faults of the robot

        Returns:
            None
        """
         self.base.ClearFaults()

    def get_cartesian(self):
        fb = self.base_cyclic.RefreshFeedback()
        pose_meters = [round(fb.base.tool_pose_x, 3), round(fb.base.tool_pose_y, 3), round(fb.base.tool_pose_z, 3),
                       round(fb.base.tool_pose_theta_x, 3), round(fb.base.tool_pose_theta_y, 3),
                       round(fb.base.tool_pose_theta_z, 3)]

        return pose_meters

    def get_joint_angles(self):       
       feedback = self.base_cyclic.RefreshFeedback()
       joints = [round(feedback.actuators[joint].position, 3) for joint in range(0, 6)]

       return joints
    
    def open_tool(self, value = 1.0):
        # Create the GripperCommand we will send
        gripper_command = Base_pb2.GripperCommand()
        finger = gripper_command.gripper.finger.add()

        # Close the gripper with position increments
        gripper_command.mode = Base_pb2.GRIPPER_POSITION
        finger.finger_identifier = 1
        finger.value = 0
        self.base.SendGripperCommand(gripper_command) #é self?

        time.sleep(value)
    
    def check_for_end_or_abort(self,error):
        def check(notification, e=error):
            if notification.action_event == Base_pb2.ACTION_END or notification.action_event == Base_pb2.ACTION_ABORT:
                e.set()

        return check


    def close_tool(self, value = 1.0):
        # Create the GripperCommand we will send
        gripper_command = Base_pb2.GripperCommand()
        finger = gripper_command.gripper.finger.add()

        # Close the gripper with position increments
        gripper_command.mode = Base_pb2.GRIPPER_POSITION
        finger.finger_identifier = 1
        finger.value = 1
        self.base.SendGripperCommand(gripper_command)  

        time.sleep(value)

        

    