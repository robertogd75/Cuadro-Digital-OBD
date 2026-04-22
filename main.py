import os
import time
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, BooleanProperty, ListProperty, StringProperty, ColorProperty
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color, Rectangle

from obd_manager import OBDManager

# Register competition font
try:
    from kivy.core.text import LabelBase
    LabelBase.register(name='RacingFont', fn_regular='C:/Windows/Fonts/consola.ttf')
except:
    pass # Fallback to default if font not found

class RealTimeGraph(Widget):
    points = ListProperty([])
    line_color = ColorProperty([1, 0, 0, 1])
    max_points = 50
    min_val = 0
    max_val = 100

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self.color_instr = Color(rgba=self.line_color)
            self.line_instr = Line(points=[], width=1.5)
        self.bind(pos=self.update_canvas, size=self.update_canvas, points=self.update_canvas)

    def add_value(self, val):
        self.points.append(val)
        if len(self.points) > self.max_points:
            self.points.pop(0)

    def update_canvas(self, *args):
        if not self.points:
            return
        
        plot_points = []
        w, h = self.size
        x, y = self.pos
        
        step_x = w / (self.max_points - 1)
        
        for i, val in enumerate(self.points):
            px = x + i * step_x
            # Normalize Y
            norm_y = (val - self.min_val) / max(1, (self.max_val - self.min_val))
            py = y + norm_y * h
            plot_points.extend([px, py])
            
        self.line_instr.points = plot_points
        self.color_instr.rgba = self.line_color

class DashboardScreen(Screen):
    rpm = NumericProperty(0)
    speed = NumericProperty(0)
    temp = NumericProperty(0)
    boost = NumericProperty(0)
    oil_temp = NumericProperty(0)
    voltage = NumericProperty(0)
    throttle = NumericProperty(0)
    iat = NumericProperty(0)
    fuel = NumericProperty(0)
    hp = NumericProperty(0)
    torque = NumericProperty(0)
    
    status_text = StringProperty("DESCONECTADO")
    status_color = ColorProperty([1, 0, 0, 1]) # Red
    
    gear = ListProperty(["N"])
    timer_text = ListProperty(["0.00"])
    shift_light = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timer_start = 0
        self.timer_active = False
        self.timer_finished = False
        Clock.schedule_interval(self.update_shift_light, 0.1)

    def update_shift_light(self, dt):
        if self.rpm > 4200:
            self.shift_light = not self.shift_light
        else:
            self.shift_light = False

    def update_logic(self, rpm, speed):
        if speed < 1:
            self.gear = ["N"]
        else:
            ratio = rpm / max(speed, 1)
            if ratio > 85: self.gear = ["1"]
            elif 55 < ratio <= 85: self.gear = ["2"]
            elif 38 < ratio <= 55: self.gear = ["3"]
            elif 25 < ratio <= 38: self.gear = ["4"]
            else: self.gear = ["5"]

        if speed > 1 and not self.timer_active and not self.timer_finished:
            self.timer_start = time.time()
            self.timer_active = True
        if self.timer_active:
            elapsed = time.time() - self.timer_start
            self.timer_text = ["{:.2f}".format(elapsed)]
            if speed >= 100:
                self.timer_active = False
                self.timer_finished = True
        if speed == 0:
            self.timer_active = False
            self.timer_finished = False
            self.timer_text = ["0.00"]

import json
from datetime import datetime

class AccelerationScreen(Screen):
    timer_val = StringProperty("0.00")
    status_msg = StringProperty("LISTO")
    mode = StringProperty("AUTO") # AUTO or MANUAL
    history = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_time = 0
        self.active = False
        self.finished = False
        self.load_history()

    def load_history(self):
        try:
            if os.path.exists("history.json"):
                with open("history.json", "r") as f:
                    self.history = json.load(f)
        except:
            self.history = []

    def save_run(self, time_val):
        timestamp = datetime.now().strftime("%d/%m %H:%M")
        new_run = {"time": f"{time_val}s", "date": timestamp}
        self.history.insert(0, new_run)
        self.history = self.history[:5] # Keep last 5
        try:
            with open("history.json", "w") as f:
                json.dump(self.history, f)
        except:
            pass

    def toggle_mode(self):
        self.mode = "MANUAL" if self.mode == "AUTO" else "AUTO"
        self.reset_timer()

    def manual_start(self):
        if self.mode == "MANUAL" and not self.active:
            self.start_time = time.time()
            self.active = True
            self.status_msg = "CONTANDO..."
            Clock.schedule_interval(self.update_timer, 0.05)

    def update_timer(self, dt):
        if self.active:
            elapsed = time.time() - self.start_time
            self.timer_val = "{:.2f}".format(elapsed)
        return self.active

    def on_speed_update(self, speed):
        # Auto start logic
        if self.mode == "AUTO" and not self.active and not self.finished:
            if speed > 0.5:
                self.start_time = time.time()
                self.active = True
                self.status_msg = "ESTADO: ¡DALE CAÑA!"
                Clock.schedule_interval(self.update_timer, 0.05)
        
        # Stop logic (Both modes)
        if self.active and speed >= 100:
            self.active = False
            self.finished = True
            self.status_msg = "ESTADO: ¡PRUEBA FINALIZADA!"
            self.save_run(self.timer_val)
            
        # Suggest reset if speed is 0 and we were finished
        if self.finished and speed < 0.5:
            self.status_msg = "ESTADO: PREPARADO"

    def reset_timer(self):
        self.active = False
        self.finished = False
        self.timer_val = "0.00"
        self.status_msg = "ESTADO: LISTO (AUTO)" if self.mode == "AUTO" else "ESTADO: ESPERANDO INICIO"

class PerformanceScreen(Screen):
    hp = NumericProperty(0)
    torque = NumericProperty(0)
    boost = NumericProperty(0)

    def update_graphs(self, hp, torque, boost):
        self.hp = hp
        self.torque = torque
        self.boost = boost
        self.ids.graph_hp.add_value(hp)
        self.ids.graph_torque.add_value(torque)
        self.ids.graph_boost.add_value(boost)

class DiagnosticsScreen(Screen):
    def refresh_dtc(self):
        app = App.get_running_app()
        dtcs = app.obd_manager.get_dtc()
        self.ids.dtc_list.clear_widgets()
        for code, desc in dtcs:
            item = Factory.DTCItem()
            item.code = code
            item.desc = desc
            self.ids.dtc_list.add_widget(item)
            
    def clear_dtc(self):
        app = App.get_running_app()
        if app.obd_manager.clear_dtc():
            self.ids.dtc_list.clear_widgets()

class OBDApp(App):
    dark_mode = BooleanProperty(True)

    def toggle_mode(self):
        self.dark_mode = not self.dark_mode

    def build(self):
        self.title = "INSTRUMENTACIÓN PROFESIONAL - 1.6 HDI"
        self.obd_manager = OBDManager()
        self.obd_manager.start(callback=self._on_obd_data)
        
        # Poll status every second for real-time UI updates
        Clock.schedule_interval(self.check_obd_status, 1.0)
        
        return Builder.load_file("dashboard.kv")

    def check_obd_status(self, dt):
        status = self.obd_manager.status
        
        # If we are not actively 'BUSCANDO...', and not connected, force 'DESCONECTADO'
        if status != "BUSCANDO...":
            if self.obd_manager.async_connection:
                if not self.obd_manager.async_connection.is_connected():
                    status = "DESCONECTADO"
            else:
                status = "DESCONECTADO"
        
        self._update_ui("STATUS", status)

    def _on_obd_data(self, key, value):
        Clock.schedule_once(lambda dt: self._update_ui(key, value))

    def _update_ui(self, key, value):
        try:
            dash = self.root.get_screen('dashboard')
        except:
            return # Screen not ready
            
        perf = self.root.get_screen('performance')
        
        if key == "STATUS":
            if dash.status_text != value: # Only update on change
                dash.status_text = value
                if value == "CONECTADO": dash.status_color = [0, 1, 0, 1]
                elif value == "BUSCANDO...": dash.status_color = [1, 1, 0, 1]
                else: 
                    dash.status_color = [1, 0, 0, 1]
                    self._reset_dashboard(dash)

        elif key == "MAF_UPDATE":
            dash.hp = float(value["HP"])
            dash.torque = float(value["TORQUE"])
            perf.update_graphs(dash.hp, dash.torque, dash.boost)
        
        elif key == "RPM":
            dash.rpm = float(value)
            dash.update_logic(dash.rpm, dash.speed)
        elif key == "SPEED":
            dash.speed = float(value)
            dash.update_logic(dash.rpm, dash.speed)
            self.root.get_screen('acceleration').on_speed_update(dash.speed)
        elif key == "BOOST":
            dash.boost = float(value)
        elif key == "COOLANT_TEMP": dash.temp = float(value)
        elif key == "OIL_TEMP": dash.oil_temp = float(value)
        elif key == "VOLTAGE": dash.voltage = float(value)
        elif key == "THROTTLE": dash.throttle = float(value)
        elif key == "IAT": dash.iat = float(value)
        elif key == "FUEL": dash.fuel = float(value)

    def _reset_dashboard(self, dash):
        dash.rpm = 0
        dash.speed = 0
        dash.boost = 0
        dash.hp = 0
        dash.torque = 0
        dash.gear = ["N"]
        dash.timer_text = ["0.00"]

    def on_stop(self):
        self.obd_manager.stop()

if __name__ == "__main__":
    OBDApp().run()
