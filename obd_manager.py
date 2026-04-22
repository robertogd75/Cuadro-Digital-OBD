import obd
import threading
import time

class OBDManager:
    def __init__(self):
        self.connection = None
        self.async_connection = None
        self.status = "DESCONECTADO" # DESCONECTADO, BUSCANDO..., CONECTADO
        self.data = {
            "RPM": 0,
            "SPEED": 0,
            "COOLANT_TEMP": 0,
            "MAP": 100, # kPa
            "BARO": 100, # kPa
            "BOOST": 0, # Bar
            "OIL_TEMP": 0,
            "VOLTAGE": 0,
            "THROTTLE": 0,
            "IAT": 0,
            "MAF": 0, # g/s
            "FUEL_LEVEL": 0, # %
            "HP": 0,
            "TORQUE": 0,
            "DTC": []
        }
        self.running = False
        self.update_callback = None

    def start(self, callback=None):
        self.update_callback = callback
        self.running = True
        self.status = "DESCONECTADO"
        threading.Thread(target=self._connect_loop, daemon=True).start()

    def _notify_status(self):
        if self.update_callback:
            self.update_callback("STATUS", self.status)

    def _connect_loop(self):
        while self.running:
            # Check if we need to reconnect
            is_connected = False
            if self.async_connection:
                is_connected = self.async_connection.is_connected()
            
            if not is_connected:
                self.status = "DESCONECTADO"
                self._connect_async()
            
            time.sleep(5) # Period check

    def _connect_async(self):
        try:
            # We stay in DESCONECTADO (Red) while scanning
            ports = obd.scan_serial()
            if not ports:
                self.status = "DESCONECTADO"
                return

            # Port found! Now we try to open it and check protocol (Yellow)
            self.status = "BUSCANDO..."
            self._notify_status()
            
            self.async_connection = obd.Async(ports[0])
            
            # Watch commands
            self.async_connection.watch(obd.commands.RPM, callback=self._on_rpm)
            self.async_connection.watch(obd.commands.MAF, callback=self._on_maf)
            self.async_connection.watch(obd.commands.SPEED, callback=self._on_speed)
            self.async_connection.watch(obd.commands.INTAKE_PRESSURE, callback=self._on_map)
            self.async_connection.watch(obd.commands.BAROMETRIC_PRESSURE, callback=self._on_baro)
            self.async_connection.watch(obd.commands.COOLANT_TEMP, callback=self._on_temp)
            self.async_connection.watch(obd.commands.OIL_TEMP, callback=self._on_oil_temp)
            self.async_connection.watch(obd.commands.CONTROL_MODULE_VOLTAGE, callback=self._on_voltage)
            self.async_connection.watch(obd.commands.THROTTLE_POS, callback=self._on_throttle)
            self.async_connection.watch(obd.commands.INTAKE_TEMP, callback=self._on_iat)
            self.async_connection.watch(obd.commands.FUEL_LEVEL, callback=self._on_fuel)
            
            self.async_connection.start()
            
            # Wait a bit for status update
            time.sleep(1)
            
            if self.async_connection.is_connected():
                self.status = "CONECTADO"
            else:
                self.status = "DESCONECTADO"
            self._notify_status()
            
        except Exception as e:
            print(f"Error connecting: {e}")
            self.status = "DESCONECTADO"
            self._notify_status()

    # Callbacks
    def _on_rpm(self, r):
        if not r.is_null():
            self.data["RPM"] = r.value.magnitude
            self._calculate_performance()
            if self.update_callback: self.update_callback("RPM", self.data["RPM"])

    def _on_maf(self, r):
        if not r.is_null():
            self.data["MAF"] = r.value.magnitude
            self._calculate_performance()
            if self.update_callback: self.update_callback("MAF_UPDATE", self.data)

    def _on_map(self, r):
        if not r.is_null():
            self.data["MAP"] = r.value.magnitude
            self._calculate_boost()
            if self.update_callback: self.update_callback("BOOST", self.data["BOOST"])

    def _on_baro(self, r):
        if not r.is_null():
            self.data["BARO"] = r.value.magnitude
            self._calculate_boost()

    def _calculate_boost(self):
        # Turbo = MAP - BARO
        self.data["BOOST"] = max(0, (self.data["MAP"] - self.data["BARO"]) / 100.0)

    def _calculate_performance(self):
        # CV = MAF / 0.8
        self.data["HP"] = self.data["MAF"] / 0.8
        # Nm = (CV * 7023) / RPM
        if self.data["RPM"] > 500:
            self.data["TORQUE"] = (self.data["HP"] * 7023) / self.data["RPM"]
        else:
            self.data["TORQUE"] = 0

    def _on_speed(self, r):
        if not r.is_null():
            self.data["SPEED"] = r.value.magnitude
            if self.update_callback: self.update_callback("SPEED", self.data["SPEED"])

    def _on_temp(self, r):
        if not r.is_null():
            self.data["COOLANT_TEMP"] = r.value.magnitude
            if self.update_callback: self.update_callback("COOLANT_TEMP", self.data["COOLANT_TEMP"])

    def _on_oil_temp(self, r):
        if not r.is_null():
            self.data["OIL_TEMP"] = r.value.magnitude
            if self.update_callback: self.update_callback("OIL_TEMP", self.data["OIL_TEMP"])

    def _on_voltage(self, r):
        if not r.is_null():
            self.data["VOLTAGE"] = r.value.magnitude
            if self.update_callback: self.update_callback("VOLTAGE", self.data["VOLTAGE"])

    def _on_throttle(self, r):
        if not r.is_null():
            self.data["THROTTLE"] = r.value.magnitude
            if self.update_callback: self.update_callback("THROTTLE", self.data["THROTTLE"])

    def _on_iat(self, r):
        if not r.is_null():
            self.data["IAT"] = r.value.magnitude
            if self.update_callback: self.update_callback("IAT", self.data["IAT"])

    def _on_fuel(self, r):
        if not r.is_null():
            self.data["FUEL_LEVEL"] = r.value.magnitude
            if self.update_callback: self.update_callback("FUEL", self.data["FUEL_LEVEL"])

    def get_dtc(self):
        if self.async_connection and self.async_connection.is_connected():
            response = self.async_connection.query(obd.commands.GET_DTC)
            if not response.is_null():
                return response.value
        return []

    def clear_dtc(self):
        if self.async_connection and self.async_connection.is_connected():
            response = self.async_connection.query(obd.commands.CLEAR_DTC)
            return not response.is_null()
        return False

    def stop(self):
        self.running = False
        if self.async_connection:
            self.async_connection.stop()
