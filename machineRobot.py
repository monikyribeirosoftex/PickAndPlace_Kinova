import random
from transitions import Machine
from transitions.extensions import GraphMachine

import  movements
from realRobot import RealRobot

i = 0

class MachineRobot(object):
    states = [
        #treat on_enter
        {'name': 'idle', 'on_exit': ['getState','connection', 'initiate']},
        {'name': 'pick', 'on_enter': ['getState', 'getMedicine']},
        {'name': 'error', 'on_enter': ['getState', 'detectError']},
        {'name': 'retry', 'on_enter': ['getState', 'decideContinue']},
        {'name': 'place', 'on_enter': ['getState', 'movePlace']},
        {'name': 'finished', 'on_enter': ['getState', 'finishedMedicine']},
         {'name': 'abort', 'on_enter': ['getState', 'finishedWithError']}
    ]

    #robot_not_in_error = 0

    transitions = [
        #treat conditions
        {'trigger': 'start', 'source': 'idle', 'dest': 'pick', 'unless': ['robotInError']},
        {'trigger': 'fail', 'source': 'pick', 'dest': 'error','conditions': ['robotInError']},
        {'trigger': 'retry_pick', 'source': 'error',  'dest': 'retry'},
        {'trigger': 'retry_decision', 'source': 'retry', 'dest': 'pick'},
        {'trigger': 'abort_retry', 'source': 'retry', 'dest': 'abort', 'conditions': ['robotInError']},
        {'trigger': 'success',   'source': 'pick', 'dest': 'place', 'unless': ['robotInError']},
        {'trigger': 'place_success', 'source': 'place', 'dest': 'finished', 'unless': ['robotInError']},
    ]

    def __init__(self, robot: RealRobot) -> None: #robot, define robot
        
        self.robot = robot
        self.__isMoving = False
        self.__robotInError = False
        self.__faultsFind = 0
        self.__toolOpenned = 0 #0 -  closed 1 - partially openned 2- totally oppened      
        self.machine = Machine(model = self, states = MachineRobot.states, transitions = MachineRobot.transitions, initial = 'idle')
        control = input()
        self.start()
             

    def connection(self):
        self.robot.connect()
    
    def robotInError(self):
        return self.__robotInError

    
    def initiate(self):
        self.__faultsFind = 0
        self.__robotInError = False
        self.robot.close_tool(2.0)
        self.__toolOpenned = 0
        self.robot.open_tool(1.0) 
        self.__toolOpenned = 1
        self.robot.move_joints(movements.BANK_MOVEMENTS_2['home_joint'])
                   
    
    def getState(self):
        print("State is {}".format(self.state))
    
    def getMedicine(self):        
        test = random.choice([True, False]) #TRUE -> PASS FALSE -> FAIL
        #test  = False #testar só erro
        if test:
            self.__robotInError = False            
            if self.__toolOpenned == 0:
                self.robot.open_tool()
                self.__toolOpenned = 1
            elif self.__toolOpenned == 2:
                self.robot.close_tool()
                self.__toolOpenned = 1
            self.robot.move_joints(movements.BANK_MOVEMENTS_2['quadrant_1'])
            self.robot.move_joints(movements.BANK_MOVEMENTS_2['front_medicine_1'])
            self.robot.move_joints(movements.BANK_MOVEMENTS_2['quadrant_1'])
            self.robot.close_tool()
            self.__toolOpenned = 0
            self.robot.move_joints(movements.BANK_MOVEMENTS_2['quadrant_1'])
            control = input()
            self.success()
        else:
            self.__robotInError = True
            control = input()
            self.fail()


    def movePlace(self):
        self.robot.move_joints(movements.BANK_MOVEMENTS_2['drop_safe_1'])
        self.robot.move_joints(movements.BANK_MOVEMENTS_2['drop_1'])        
        self.robot.open_tool()
        self.__toolOpenned = 1
        self.robot.move_joints(movements.BANK_MOVEMENTS_2['drop_safe_1'])
        self.robot.move_joints(movements.BANK_MOVEMENTS_2['after_recoil'])
        self.robot.move_joints(movements.BANK_MOVEMENTS_2['home_joint'])
        control = input()
        self.place_success()
    
    def finishedMedicine(self):
        print("Pick and place completed successfully")           
      

    def detectError(self):
        self.__faultsFind =  self.__faultsFind + 1
        control = input()
        self.retry_pick()
        
    
    def decideContinue(self):
        if self.__faultsFind == 3:
            control = input()
            self.abort_retry() 
        else:
            control = input()
            self.retry_decision() 
    
    def finishedWithError(self):
        print("Retry limit reached. Operation aborted")
        control = input()
        self.to_idle()

 