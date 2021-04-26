from ScopeFoundry.base_app import BaseMicroscopeApp
from ScopeFoundryHW.dynamixel_servo.dynamixel_x_servo_hw import DynamixelXServosHW
from ScopeFoundryHW.dynamixel_servo.dynamixel_filter_wheel_hw import DynamixelFilterWheelHW


class ServoTestApp(BaseMicroscopeApp):
    
    def setup(self):
        
        servos = self.add_hardware(DynamixelXServosHW(self, devices=dict(test2=2)))
        filter_wheel = self.add_hardware(DynamixelFilterWheelHW(self,
                                         named_positions={'empty': 0.0,
                                                          '1064_BP': 60, 
                                                          '950_SP': 120}
                                         )
                                                                                  
)
        servos.settings['port'] = 'COM13'
        
if __name__ == '__main__':

    app = ServoTestApp([])
    app.exec_()