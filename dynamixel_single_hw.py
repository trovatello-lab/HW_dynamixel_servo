from functools import partial

from ScopeFoundry.hardware import HardwareComponent


class DynamixelServoHW(HardwareComponent):

    name = "test2"

    def __init__(
        self,
        app,
        debug=False,
        name=None,
        lq_kwargs={"spinbox_decimals": 2, "unit": "deg"},
        scale_value=360.0 / 4096,
    ):
        self.lq_kwargs = lq_kwargs
        self.scale_value = scale_value
        HardwareComponent.__init__(self, app, debug=debug, name=name)

    def setup(self):

        S = self.settings
        S.New("dynamixel_hw", initial="dynamixel_servos", dtype=str)
        S.New("servo_name", initial=self.name, dtype=str)
        S.New(
            "mode",
            initial="position",
            dtype=str,
            choices=["extended_position", "position"],
        )
        S.New("reverse", initial=False, dtype=bool)

        S.New("target_steps", unit="steps", protected=True, dtype=int)
        S.New("steps", unit="steps", dtype=int, initial=10, ro=True)
        S.New("jog_steps", initial=114, dtype=int, unit="steps")

        S.New("target_position", dtype=float, protected=True, **self.lq_kwargs)
        S.New("position", dtype=float, ro=True, **self.lq_kwargs)
        S.New("jog", initial=10, **self.lq_kwargs)

        S.New("offset", unit="steps", dtype=int)
        S.New(
            "scale",
            initial=self.scale_value,
            spinbox_decimals=6,
            unit="/".join((S.position.unit, S.steps.unit)),
        )

        self.add_operation("jog fwd", self.jog_fwd)
        self.add_operation("jog bkwd", self.jog_bkwd)
        self.add_operation("Zero Position", self.zero_position)

        S.mode.add_listener(self.set_mode)

    def connect(self):

        S = self.settings
        servos = self.servos = self.app.hardware[S["dynamixel_hw"]]
        servos.settings["connected"] = True

        for servo_pos, steps in zip(
            [
                servos.settings.get_lq(S["servo_name"] + "_position"),
                servos.settings.get_lq(S["servo_name"] + "_target_position"),
            ],
            [S.steps, S.target_steps],
        ):
            steps.connect_lq_math(servo_pos, self.fromServo, self.toServo)

        # scaled quantities
        for p, s in zip([S.position, S.target_position], [S.steps, S.target_steps]):
            p.connect_lq_math(s, self.steps2position, self.position2steps)
        S.jog.connect_lq_scale(S.jog_steps, S["scale"])

        self.set_mode()

    def set_mode(self):
        # TODO Check if torque is enabled before enable/disable
        if not hasattr(self, "servos"):
            return
        S = self.settings
        self.servos.settings[S["servo_name"] + "_torque"] = False
        self.servos.settings[S["servo_name"] + "_oper_mode"] = S["mode"]
        self.servos.settings[S["servo_name"] + "_torque"] = True

    def jog_fwd(self):
        S = self.settings
        S["target_steps"] = S["steps"] + S["jog_steps"]

    def jog_bkwd(self):
        S = self.settings
        S["target_steps"] = S["steps"] - S["jog_steps"]

    def jog_fwd_pos(self, delta):
        S = self.settings
        S["target_position"] = S["position"] + delta

    def jog_bkwd_pos(self, delta):
        S = self.settings
        S["target_position"] = S["position"] - delta

    def min_jog(self):
        self.settings["jog_steps"] = 1

    def zero_position(self):
        if not hasattr(self, "servos"):
            return
        S = self.settings
        S["offset"] = S["steps"]
        S["target_position"] = 0
        self.servos.settings.get_lq(S["servo_name"] + "_position").read_from_hardware()

    def position2steps(self, scaled_steps):
        offset = self.settings["offset"]
        scale = self.settings["scale"]
        m = {"position": 4096, "extended_position": 2**32}[self.settings["mode"]]
        return (int(scaled_steps / scale) + offset) % m

    def steps2position(self, steps):
        offset = self.settings["offset"]
        scale = self.settings["scale"]
        # m = {'position':scale*4096,
        #     'extended_position':scale*2**32}[self.settings['mode']]
        return (steps - offset) * scale

    def fromServo(self, servo_pos):
        sign = {True: -1, False: 1}[self.settings["reverse"]]
        if self.settings["mode"] == "position":
            return (sign * servo_pos) % 4096
        return sign * servo_pos

    def toServo(self, steps):
        sign = {True: -1, False: 1}[self.settings["reverse"]]
        if self.settings["mode"] == "position":
            return (sign * steps) % 4096
        return sign * steps

    def disconnect(self):
        pass

    def New_quick_UI(
        self, target_positions=(1, 90, 180, 270), jog_sizes=(1, 5, 10, 50, 100)
    ):
        from qtpy import QtWidgets

        from ScopeFoundry.helper_funcs import load_qt_ui_file, sibling_path

        ui = load_qt_ui_file(sibling_path(__file__, "quick.ui"))
        ui.setTitle(self.name)
        s = self.settings

        s.connected.connect_to_widget(ui.power_wheel_connected_checkBox)
        s.position.connect_to_widget(ui.power_wheel_position_label)

        s.target_position.connect_to_widget(ui.target_position)
        for tpos in target_positions:
            btn = QtWidgets.QPushButton(f"{tpos}")
            btn.setStyleSheet("QPushButton {font-weight: bold;}")
            btn.setToolTip(f"move to {tpos}")
            ui.target_position_layout.addWidget(btn)
            btn.clicked.connect(partial(s.target_position.update_value, new_val=tpos))

        fwd_layout = QtWidgets.QVBoxLayout()
        bwd_layout = QtWidgets.QVBoxLayout()
        for jog_size in jog_sizes:
            btn = QtWidgets.QPushButton(f"+{jog_size}")
            btn.setStyleSheet("QPushButton {color: #360213;}")
            btn.clicked.connect(partial(self.jog_fwd_pos, delta=jog_size))
            fwd_layout.addWidget(btn)
            btn = QtWidgets.QPushButton(f"-{jog_size}")
            btn.setStyleSheet("QPushButton {color: #0d082e;}")
            btn.clicked.connect(partial(self.jog_bkwd_pos, delta=jog_size))
            bwd_layout.addWidget(btn)
        ui.horizontal_layout.addLayout(bwd_layout)
        ui.horizontal_layout.addLayout(fwd_layout)

        return ui

    def New_mini_UI(self, jog_sizes=(2, 5, 10, 50, 100)):
        from ScopeFoundry.helper_funcs import load_qt_ui_file, sibling_path

        ui = load_qt_ui_file(sibling_path(__file__, "mini.ui"))
        s = self.settings
        s.connected.connect_to_widget(ui.connected_checkBox)
        s.position.connect_to_widget(ui.position_doubleSpinBox)
        s.target_position.connect_to_widget(ui.target_position_doubleSpinBox)
        s.jog.connect_to_widget(ui.jog_doubleSpinBox)
        ui.foreward_pushButton.clicked.connect(self.jog_fwd)
        ui.backward_pushButton.clicked.connect(self.jog_bkwd)
        ui.connected_checkBox.setText(self.name)
        if jog_sizes is None:
            return ui

        from qtpy import QtWidgets

        fwd_layout = QtWidgets.QHBoxLayout()
        bwd_layout = QtWidgets.QHBoxLayout()
        for jog_size in jog_sizes:
            btn = QtWidgets.QPushButton(f"+{jog_size}")
            btn.clicked.connect(partial(self.jog_fwd_pos, delta=jog_size))
            fwd_layout.addWidget(btn)
            btn = QtWidgets.QPushButton(f"-{jog_size}")
            btn.clicked.connect(partial(self.jog_bkwd_pos, delta=jog_size))
            bwd_layout.addWidget(btn)
        ui.vertical_layout.addLayout(fwd_layout)
        ui.vertical_layout.addLayout(bwd_layout)
        return ui
