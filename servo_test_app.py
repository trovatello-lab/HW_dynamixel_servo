from ScopeFoundry.base_app import BaseMicroscopeApp
from ScopeFoundryHW.dynamixel_servo.dynamixel_x_servo_hw import DynamixelXServosHW
from ScopeFoundryHW.dynamixel_servo.dynamixel_filter_wheel_hw import DynamixelFilterWheelHW
from ScopeFoundryHW.dynamixel_servo.dynamixel_linear_hw import DynamixelLinearHW


class ServoTestApp(BaseMicroscopeApp):
    
    name = 'servo_test_app'
    
    def setup(self):
        
        servos = self.add_hardware(DynamixelXServosHW(self, devices=dict(test2=2)))
        #filter_wheel = self.add_hardware(DynamixelFilterWheelHW(self,
        #                                 named_positions={'empty': 0.0,
        #                                                  '1064_BP': 60, 
        #                                                  '950_SP': 120}
        #                                 ))
                                                                
        self.add_hardware(DynamixelLinearHW(self))

        from confocal_measure.auto_focus import AutoFocusMeasure
        self.add_measurement(AutoFocusMeasure(self))

                                                                                  
        servos.settings['port'] = 'COM11'
        
if __name__ == '__main__':

    import sys
    app = ServoTestApp(sys.argv)
    sys.exit(app.exec_())