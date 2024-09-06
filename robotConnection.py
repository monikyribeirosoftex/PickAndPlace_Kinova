import argparse

from kortex_api.TCPTransport import TCPTransport
from kortex_api.UDPTransport import UDPTransport
from kortex_api.RouterClient import RouterClient, RouterClientSendOptions
from kortex_api.SessionManager import SessionManager
from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.client_stubs.BaseCyclicClientRpc import BaseCyclicClient
from kortex_api.autogen.client_stubs.DeviceConfigClientRpc import DeviceConfigClient
from kortex_api.autogen.client_stubs.GripperCyclicClientRpc import GripperCyclicClient
from kortex_api.autogen.messages import Session_pb2

def parseConnectionArguments(parser = argparse.ArgumentParser()):
    parser.add_argument("--ip", type=str, help="IP address of destination", default="192.168.1.10")
    parser.add_argument("-u", "--username", type=str, help="username to login", default="admin")
    parser.add_argument("-p", "--password", type=str, help="password to login", default="admin")
    return parser.parse_args()

class RobotConnection():
    
    """
    Class that manages connection
    """
    TCP_PORT = 10000
    UDP_PORT = 10001
    BASE_CLIENT = None
    BASE_CYCLIC_CLIENT = None
    GRIPPER_CYCLIC_CLIENT = None
    DEVICE_CONFIG_CLIENT = None

    @staticmethod
    def createTcpConnection(ip: str = "192.168.2.10",
                                username: str = "admin",
                                password: str = "admin"): 
        """
        returns RouterClient required to create services and send requests to device or sub-devices,
        """

        return RobotConnection(ip, port=RobotConnection.TCP_PORT, credentials=(username, password))
    @staticmethod
    def createUdpConnection(ip: str = "192.168.2.10",
                                username: str = "admin",
                                password: str = "admin"): 
        """        
        returns RouterClient that allows to create services and send requests to a device or its sub-devices @ 1khz.
        """

        return RobotConnection(ip, port=RobotConnection.TCP_PORT, credentials=(username, password))

    def __init__(self, ipAddress, port=TCP_PORT, credentials = ("","")):

        self.router = None
        self.transport = None
        self.device_config = None
        self.base_cyclic = None
        self.gripper = None
        self.base = None
        self.ipAddress = ipAddress
        self.port = port
        self.credentials = credentials

        self.session_manager = None
    def connect(self):
        """
        Method responsible for connecting robot
        """
        self.transport = TCPTransport() if self.port == RobotConnection.TCP_PORT else UDPTransport()

        self.router = RouterClient(self.transport, RouterClient.basicErrorCallback)

        self.transport.connect(self.ipAddress, self.port)

        if self.credentials[0] != "":
            session_info = Session_pb2.CreateSessionInfo()
            session_info.username = self.credentials[0]
            session_info.password = self.credentials[1]
            session_info.session_inactivity_timeout = 40000  # (milliseconds)
            session_info.connection_inactivity_timeout = 20000  # (milliseconds)

            self.session_manager = SessionManager(self.router)
            print("Logging as", self.credentials[0], "on device", self.ipAddress)
            self.session_manager.CreateSession(session_info)
        else:
            raise Exception("No credentials provided")

        return

    def disconnect(self):
        """
        Method responsible for disconnecting robot, by closing
        SessionManager object and all connected devices.
        """

        session_manager_is_valid = self.session_manager is not None
        transport_is_valid = self.transport is not None

        if not transport_is_valid:
            return

        if session_manager_is_valid:
            router_options = RouterClientSendOptions()
            router_options.timeout_ms = 100

            self.session_manager.CloseSession(router_options)

        self.transport.disconnect()

    @classmethod
    def client_exists(cls, client_str: str) -> bool:
        """
        Deals with the verification of all devices client,
        guarantying no second instantiation, which avoids callback error list.
        The devices client should be class attributes, defined only once, after first connection.

        :return: True if there's already a device client connected
        """
        client = getattr(cls, client_str)
        if client is not None:
            return True
        return False
        
    def create_base_client(self):
        if self.client_exists("BASE_CLIENT"):
            return
        RobotConnection.BASE_CLIENT = BaseClient(self.router)

    def get_base_client(self) -> BaseClient:
        self.check_router_connection()
        self.create_base_client()
        return RobotConnection.BASE_CLIENT

    def get_gripper_cyclic_client(self) -> GripperCyclicClient:
        self.check_router_connection()
        return GripperCyclicClient(self.router)

    def get_base_cyclic_client(self) -> BaseCyclicClient:
        self.check_router_connection()

        return BaseCyclicClient(self.router)

    def get_device_config_client(self) -> DeviceConfigClient:
        self.check_router_connection()
        return DeviceConfigClient(self.router)

    def check_router_connection(self):
        if self.router is None:
            msg = "Empty router object. Make sure there is a router object available."
            raise Exception(msg)


if __name__ == "__main__":
    robot_connection = RobotConnection("192.168.2.11")
    print(robot_connection)