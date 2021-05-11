'''
Created on Apr 26, 2021

@author: Benedikt Ursprung
'''
from ScopeFoundry.hardware import HardwareComponent
import time

class DynamixelFilterWheelHW(HardwareComponent):
    
    name = 'filter_wheel'
    
    def __init__(self, app, debug=False, name=None, 
                 named_positions={'Other':0}, 
                 positions_in_degrees=False,
                 release_at_target=False,
                 ):
                             
        if positions_in_degrees:
            self.named_positions = {}
            for pos,deg in named_positions.items():
                self.named_positions.update({pos:int(deg*4096/360)})
        else: 
            self.named_positions = named_positions
            
        self.release_at_target = release_at_target                   
        HardwareComponent.__init__(self, app, debug=debug, name=name)
        
        
    def setup(self):
        
        S = self.settings
        S.New('dynamixel_hw', initial='dynamixel_servos', dtype=str)
        S.New('servo_name', initial=self.name, dtype=str)
        S.New('offset', initial=0, unit='steps', dtype=int)
        S.New('position', unit='steps', dtype=int)

        S.New('target_position', unit='steps', dtype=int)
        S.New('release_at_target', dtype=bool, initial=self.release_at_target)
        
        if type(self.named_positions) == dict:
            self.settings.New('named_position', dtype=str, 
                              initial = list(self.named_positions.keys())[0],
                              choices = tuple(self.named_positions.keys()) )
            
            for name, pos in self.named_positions.items():
                self.add_operation('Goto '+name, lambda name=name: self.settings.named_position.update_value(name))
                
        self.add_operation('set offset', self.set_offset)
        
    def connect(self):
        
        S = self.settings
        servos = self.servos = self.app.hardware[S['dynamixel_hw']]
        servos.settings['connected'] = True

        # set mode to extended_position
        servos.settings[S['servo_name']+'_torque'] = False
        servos.settings[S['servo_name']+'_mode'] = 4
        servos.settings[S['servo_name']+'_torque'] = True # unexpected behavior if not enabled
        
        S.target_position.connect_lq_scale(
            servos.settings.get_lq(S['servo_name']+'_target_position'), scale=1) #NOTE, not disconnected on disconnect       

        S.position.connect_lq_scale(
            servos.settings.get_lq(S['servo_name']+'_position'), scale=1) #NOTE, not disconnected on disconnect       
          
        if 'named_position' in self.settings:
            self.settings.named_position.connect_to_hardware(
                write_func=self.goto_named_position
                )
        
    def disconnect(self):
        pass
        
    def goto_named_position(self, name):
        S = self.settings
        if name != 'Other':
            self.servos.settings[S['servo_name']+'_torque'] = True
            self.settings['target_position'] = self.named_positions[name] + S['offset']

            if S['release_at_target']:
                time.sleep(0.8)  # ToDo: instead of waiting, check if is moving
                self.servos.settings[S['servo_name']+'_torque'] = False
                                   
            
    def set_offset(self):
        current_position = self.servos.settings[self.settings['servo_name']+'_position']
        self.settings['offset'] = current_position
        


        

        