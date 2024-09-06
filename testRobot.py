import keyboard
from abstractRobot import AbstractRobot


class TestRobot(AbstractRobot):

    #init
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
        self.trajectory_info = None
        

    def move_to_home(self):
        print(f"Move to home")

    def connect(self, connection_ip: str = "192.168.2.10"):
       print("Connecting test in {connection_ip}")


    def request_devices_services(self) -> None:
        print("Requesting devices services...")

    def disconnect(self):
        print(f"Disconnect robot")
        self.device = None
        self.base = None

    def move_cartesian(self, pose_list: list[float]):
        # Starting Cartesian action movement
        print(f"Move cartesian in {pose_list}")
        
    def move_joints(self, joints_list: list[float]):
        print(f"Move joints in {joints_list}")
    
    def apply_emergency_stop(self):
        print("Aplying emergency stop")

    def clear_faults(self):
         print("Cleaning faults")
         self.error_number = 0

    def get_cartesian(self):
        print('Getting cartesian angles...')
        return [0, 0, 0, 0, 0, 0]

    def get_joint_angles(self, joints_list):       
       print('Getting joint angles...')
       return [0, 0, 0, 0, 0, 0]
    
    def open_tool(self, value = 1.0):
        print(f"Opening tool in {value}")

    def close_tool(self, value = 1.0):
        print(f"Closing tool in {value}")

        


if __name__ == '__main__':

    #the = threading()
    robot = TestRobot()

    
