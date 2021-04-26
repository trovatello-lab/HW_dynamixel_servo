'''
Created on Apr 26, 2021

@author: Benedikt Ursprung
'''
from ScopeFoundry.hardware import HardwareComponent


class DynamixelFilterWheelHW(HardwareComponent):
    
    name = 'filter_wheel'
    
    def __init__(self, app, debug=False, name='filter_wheel', named_positions={'Other':0}):
        """ named_positions is a dictionary of names:positions(in degrees)
        """
                 
        self.named_positions = named_positions
        HardwareComponent.__init__(self, app, debug=debug, name=name)
        
        
    def setup(self):
        
        S = self.settings
        S.New('dynamixel_hw', initial='dynamixel_servos', dtype=str)
        S.New('servo_name', initial='test2', dtype=str)
        S.New('offset', initial=0, unit='steps', dtype=int)
        S.New('target_position', unit='steps', dtype=int)
        
        
        if type(self.named_positions) == dict:
            self.settings.New('named_position', dtype=str, 
                              initial = list(self.named_positions.keys())[0],
                              choices = tuple(self.named_positions.keys()) )
            
            for name, pos in self.named_positions.items():
                self.add_operation('Goto '+name, lambda name=name: self.settings.named_position.update_value(name))
                
        self.add_operation('update_offset', self.update_offset)
        
    def connect(self):
        
        S = self.settings
        servos = self.servos = self.app.hardware[S['dynamixel_hw']]
        servos.settings['connected'] = True
        S.target_position.connect_lq_scale( servos.settings.get_lq(S['servo_name']+'_target_position'), scale=1)
        
        if 'named_position' in self.settings:
            self.settings.named_position.connect_to_hardware(
                write_func=self.goto_named_position
                )
        
    def disconnect(self):
        pass
        
        
    def goto_named_position(self, name):
        if name != 'Other':
            print('go_to')
            self.set_target_position_deg(self.named_positions[name])                      
            
    def update_offset(self):
        current_position = self.servos.settings[self.settings['servo_name']+'_position']
        self.settings['offset'] = current_position
        
        
    def set_target_position_deg(self, deg):
        steps = ( int(4096*deg/360) + self.settings['offset'] ) % 4096
        self.settings['target_position'] = steps        