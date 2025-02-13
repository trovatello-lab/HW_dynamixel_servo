from ScopeFoundry.base_app import BaseMicroscopeApp


class ServoTestApp(BaseMicroscopeApp):

    name = "servo_test_app"

    def setup(self):

        from ScopeFoundryHW.robotis_dynamixel_servo import DynamixelXServosHW
        from ScopeFoundryHW.robotis_dynamixel_servo import DynamixelFilterWheelHW
        from ScopeFoundryHW.robotis_dynamixel_servo import DynamixelServoHW

        servos = self.add_hardware(
            DynamixelXServosHW(self, devices=dict(reflector_wheel=51, test_wheel=51))
        )

        self.add_hardware(
            DynamixelFilterWheelHW(
                self,
                name="reflector_wheel",
                named_positions={
                    "empty": (90, "lightgreen"),
                    "mirror": (180, "yellowgreen"),
                    "glass": (270, "lime"),
                },
            )
        )

        self.add_hardware(DynamixelServoHW(self, name="test_wheel"))

        servos.settings["port"] = "COM10"
        servos.settings["connected"] = True

    def setup_ui(self):
        from qtpy import QtWidgets

        widget = QtWidgets.QWidget()
        widget.setMaximumWidth(380)
        layout = QtWidgets.QVBoxLayout(widget)
        self.add_quickbar(widget)
        layout.addWidget(self.hardware["test_wheel"].New_mini_UI())
        layout.addWidget(self.hardware["test_wheel"].New_quick_UI())


if __name__ == "__main__":

    import sys

    app = ServoTestApp(sys.argv)
    # app.qtapp.setStyle('Fusion')
    sys.exit(app.exec_())
