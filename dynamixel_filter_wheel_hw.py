'''
Created on Apr 26, 2021

@author: Benedikt Ursprung
'''
from ScopeFoundry.hardware import HardwareComponent

class DynamixelFilterWheelHW(HardwareComponent):
    
    name = 'filter_wheel'
    
    def __init__(self, app, debug=False, name='filter_wheel', named_positions={'Other':0}):
                 
        self.named_positions = named_positions
        HardwareComponent.__init__(self, app, debug=debug, name=name)
        
        
    def setup(self):
        
        S = self.settings
        S.New('dynamixel_hw', initial='dynamixel_servos', dtype=str)
        S.New('servo_name', initial='test2', dtype=str)
        S.New('offset', initial=0, unit='steps', dtype=int)

        S.New('position', unit='steps', dtype=int)
        S.New('deg', unit='deg', dtype=float)

        S.New('target_position', unit='steps', dtype=int)
        S.New('target_deg', unit='deg', dtype=float)
        
        if type(self.named_positions) == dict:
            self.settings.New('named_position', dtype=str, 
                              initial = list(self.named_positions.keys())[0],
                              choices = tuple(self.named_positions.keys()) )
            
            for name, pos in self.named_positions.items():
                self.add_operation('Goto '+name, lambda name=name: self.settings.named_position.update_value(name))
                
        self.add_operation('zero position', self.zero_position)
        
    def connect(self):
        
        S = self.settings
        servos = self.servos = self.app.hardware[S['dynamixel_hw']]
        servos.settings['connected'] = True

        servos.settings[S['servo_name']+'_torque'] = False # unexpected behavior if not enabled
        servos.settings[S['servo_name']+'_mode'] = 3 #'position'
        servos.settings[S['servo_name']+'_torque'] = True # unexpected behavior if not enabled
        
        S.target_position.connect_lq_scale(
            servos.settings.get_lq(S['servo_name']+'_target_position'), scale=1) #NOTE, not disconnected on disconnect       
        S.target_deg.connect_lq_math(S.target_position, self.steps2deg, 
                                     self.deg2steps)

        S.position.connect_lq_scale(
            servos.settings.get_lq(S['servo_name']+'_position'), scale=1) #NOTE, not disconnected on disconnect       
        S.deg.connect_lq_math(S.position, self.steps2deg, 
                                     self.deg2steps)
          
        if 'named_position' in self.settings:
            self.settings.named_position.connect_to_hardware(
                write_func=self.goto_named_position
                )
        
    def disconnect(self):
        pass
        
    def goto_named_position(self, name):
        if name != 'Other':
            self.settings['target_deg'] = self.named_positions[name]                      
            
    def zero_position(self):
        current_position = self.servos.settings[self.settings['servo_name']+'_position']
        self.settings['offset'] = current_position
                
    def steps2deg(self, steps):
        offset = self.settings['offset']
        return ( (steps - offset) *360./4096. ) % 360
    
    def deg2steps(self, deg):
        offset = self.settings['offset']
        return ( int(4096*deg/360) + offset ) % 4096
        
        
    
        

        