"""
The Advanced Rocket Simulator is a Python-based application designed for simulating rocket trajectories and dynamics. Built with a blend of PyQt5 for GUI development and PyVista for 3D visualization, this simulator offers a detailed and interactive way to study rocket mechanics.

Development Insights:
1 = GUI Development: The application utilizes PyQt5 to create an intuitive and feature-rich graphical user interface. It includes multiple tabs for simulation settings, real-time plotting, and log management, enhancing user experience and accessibility.

2 = 3D Visualization: PyVista is integrated into the simulator for 3D model visualization, allowing users to load and inspect rocket designs. This feature helps in understanding the spatial aspects of the rockets.

3 = Simulation Parameters: The simulator includes adjustable parameters such as thrust, gravity, mass, drag coefficient, and environmental conditions (temperature, humidity, wind speed). These can be modified in real-time, providing a dynamic simulation environment.

4 = Graphical Analysis: Users can select different graph types like altitude vs. time, velocity vs. time, and acceleration vs. time to visualize simulation data, aiding in detailed analysis and learning.

Follow My Journey:
Instagram: https://www.instagram.com/creativeindia__/
Facebook: https://www.facebook.com/profile.php?id=100052831652668&mibextid=ZbWKwL
YouTube: https://www.youtube.com/@PROJECTOCCUPYMARS
"""




import sys
import json
import numpy as np
import pyttsx3
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QTabWidget,
                             QToolTip, QMenuBar, QMenu, QAction, QMessageBox, QComboBox, QFrame, QFontDialog, QFileDialog,
                             QSlider, QCheckBox, QGridLayout, QProgressBar, QTextEdit)
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QTimer
# from PyQt5.QtOpenGL import QGLWidget
# from OpenGL.GL import *
# from OpenGL.GLU import gluPerspective
import pyvista as pv
from pyvistaqt.plotting import QVTKRenderWindowInteractor




class RocketSimulator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.simulation_running = False
        self.simulation_paused = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_simulation)
        self.tts_engine = pyttsx3.init()
        self.plotter = None

    def initUI(self):
        self.setFixedSize(1200, 900)
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setWindowTitle('Advanced Rocket Simulator (Pie.Space)')

        # Menu bar for theme, font selection, file operations, and advanced options
        menu_bar = QMenuBar(self)
        theme_menu = QMenu('Theme', self)
        font_menu = QMenu('Font', self)
        file_menu = QMenu('File', self)
        advanced_menu = QMenu('Advanced', self)
        menu_bar.addMenu(theme_menu)
        menu_bar.addMenu(font_menu)
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(advanced_menu)

        # Settings Tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()

        # Add a button to open the file to visualize the 3D model
        # self.load_model_button = QPushButton("Load 3D Model", self)
        # self.load_model_button.clicked.connect(self.load_3d_model)
        # settings_layout.addWidget(self.load_model_button)



        # Theme actions
        theme_action_black = QAction('Black', self)
        theme_action_black.triggered.connect(self.set_black_theme)
        theme_menu.addAction(theme_action_black)

        theme_action_white = QAction('White', self)
        theme_action_white.triggered.connect(self.set_white_theme)
        theme_menu.addAction(theme_action_white)

        theme_action_system = QAction('System', self)
        theme_action_system.triggered.connect(self.set_system_theme)
        menu_bar.addAction(theme_action_system)

        # Font actions
        font_size_action = QAction('Set Font Size', self)
        font_size_action.triggered.connect(self.set_font_size)
        font_menu.addAction(font_size_action)

        font_style_action = QAction('Set Font Style', self)
        font_style_action.triggered.connect(self.set_font_style)
        font_menu.addAction(font_style_action)

        # File actions
        save_config_action = QAction('Save Configuration', self)
        save_config_action.triggered.connect(self.save_configuration)
        file_menu.addAction(save_config_action)

        load_config_action = QAction('Load Configuration', self)
        load_config_action.triggered.connect(self.load_configuration)
        file_menu.addAction(load_config_action)

        # Advanced options
        log_data_action = QAction('Log Data', self)
        log_data_action.triggered.connect(self.toggle_data_logging)
        advanced_menu.addAction(log_data_action)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setMenuBar(menu_bar)

        # Tab widget
        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # Simulation Tab
        sim_tab = QWidget()
        sim_layout = QVBoxLayout()

        # Title
        title_label = QLabel('Advanced Rocket Simulator Pie.Space', self)
        title_label.setFont(QFont('SansSerif', 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        sim_layout.addWidget(title_label)

        # Add a button to load the 3D model using PyVista
        self.load_model_button_pyvista = QPushButton("Load 3D Model (PyVista)", self)
        self.load_model_button_pyvista.clicked.connect(self.load_3d_model_pyvista)
        sim_layout.addWidget(self.load_model_button_pyvista)


        # Add PyVista plotter
        # self.vtk_widget = QVTKRenderWindowInteractor(self)
        # sim_layout.addWidget(self.vtk_widget)

        self.vtk_widget = QWidget(self)
        vtk_layout = QVBoxLayout(self.vtk_widget)
        sim_layout.addWidget(self.vtk_widget)

        sim_tab.setLayout(sim_layout)
        tabs.addTab(sim_tab , "Simulation")


        # Grid layout for rocket parameters
        param_frame = QFrame(self)
        param_frame.setFrameShape(QFrame.Box)
        param_frame.setFrameShadow(QFrame.Raised)
        param_frame.setStyleSheet("background-color: lightgreen;")
        grid_layout = QGridLayout()
        self.inputs = {}
        params = [
            ("Thrust (N)", "Force produced by the rocket engines. Example: 20000."),
            ("Gravity (m/s^2)", "Acceleration due to gravity. Example: 9.81 for Earth."),
            ("Dry Mass (kg)", "Mass of the rocket without fuel. Example: 800."),
            ("Wet Mass (kg)", "Mass of the rocket with fuel. Example: 1500."),
            ("Length (m)", "Length of the rocket. Example: 10."),
            ("Diameter (m)", "Diameter of the rocket. Example: 1."),
            ("Material", "Material of the rocket. Example: Aluminum."),
            ("Specific Impulse (s)", "Specific impulse of the rocket engine. Example: 300."),
            ("Launch Angle (degrees)", "Angle of launch. Example: 45."),
            ("Avionics Weight (kg)", "Weight of the avionics. Example: 50."),
            ("Initial Velocity (m/s)", "Initial velocity of the rocket. Example: 0."),
            ("Initial Acceleration (m/s^2)", "Initial acceleration of the rocket. Example: 0."),
            ("Drag Coefficient (Cd)", "Drag coefficient, typical values range from 0.3 to 0.5."),
            ("Atmospheric Density (kg/m^3)", "Density of air at the launch site. Example: 1.225 at sea level."),
            ("Fuel Burn Rate (kg/s)", "Rate at which fuel is consumed. Example: 5."),
            ("Wind Speed (m/s)", "Speed of the wind. Example: 5."),
            ("Temperature (C)", "Ambient temperature. Example: 20."),
            ("Humidity (%)", "Relative humidity. Example: 50."),
        ]

        row = 0
        col = 0
        for param, tooltip in params:
            label = QLabel(param)
            line_edit = QLineEdit()
            line_edit.setToolTip(tooltip)
            grid_layout.addWidget(label, row, col)
            grid_layout.addWidget(line_edit, row, col + 1)
            self.inputs[param] = line_edit
            col += 2
            if col >= 4:
                row += 1
                col = 0

        param_frame.setLayout(grid_layout)
        sim_layout.addWidget(param_frame)

        # Simulation controls
        control_layout = QHBoxLayout()
        self.run_button = QPushButton("Run", self)
        # self.run_button.setIcon(QIcon("path/to/run_icon.png"))  # Add your icon path
        self.run_button.setToolTip("Start the simulation")
        self.run_button.clicked.connect(self.run_simulation)
        control_layout.addWidget(self.run_button)

        self.pause_button = QPushButton("Pause", self)
        # self.pause_button.setIcon(QIcon("path/to/pause_icon.png"))  # Add your icon path
        self.pause_button.setToolTip("Pause the simulation")
        self.pause_button.clicked.connect(self.pause_simulation)
        control_layout.addWidget(self.pause_button)

        self.stop_button = QPushButton("Stop", self)
        # self.stop_button.setIcon(QIcon("path/to/stop_icon.png"))  # Add your icon path
        self.stop_button.setToolTip("Stop the simulation")
        self.stop_button.clicked.connect(self.stop_simulation)
        control_layout.addWidget(self.stop_button)

        sim_layout.addLayout(control_layout)

        # Add a dropdown for graph type selection
        self.graph_type_combo = QComboBox(self)
        self.graph_type_combo.addItems(["Altitude vs Time", "Velocity vs Time", "Acceleration vs Time", "3D Trajectory"])
        sim_layout.addWidget(self.graph_type_combo)

        # Add a slider for simulation speed control
        self.speed_slider = QSlider(Qt.Horizontal, self)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(10)
        self.speed_slider.setTickInterval(10)
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        sim_layout.addWidget(QLabel("Simulation Speed:"))
        sim_layout.addWidget(self.speed_slider)

        # Add a checkbox for real-time plotting
        self.real_time_checkbox = QCheckBox("Real-time Plotting", self)
        sim_layout.addWidget(self.real_time_checkbox)

        # Add a progress bar with custom styling
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("QProgressBar {border: 2px solid grey; border-radius: 5px; text-align: center;}"
                                        "QProgressBar::chunk {background-color: #05B8CC; width: 20px;}")
        self.progress_bar.setVisible(False)
        sim_layout.addWidget(self.progress_bar)

        # Add OpenGL Widget for 3D Visualization
        # self.opengl_widget = OpenGLWidget(self)
        # sim_layout.addWidget(self.opengl_widget)

        sim_tab.setLayout(sim_layout)
        tabs.addTab(sim_tab, "Simulation")

        # Graph Tab
        graph_tab = QWidget()
        graph_layout = QVBoxLayout()

        graph_controls_layout = QHBoxLayout()
        self.save_graph_button = QPushButton("Save Graph", self)
        self.save_graph_button.setToolTip("Save the current graph as an image")
        self.save_graph_button.clicked.connect(self.save_graph)
        graph_controls_layout.addWidget(self.save_graph_button)
        self.zoom_in_button = QPushButton("Zoom In", self)
        self.zoom_in_button.setToolTip("Zoom into the graph")
        self.zoom_in_button.clicked.connect(self.zoom_in_graph)
        graph_controls_layout.addWidget(self.zoom_in_button)
        self.zoom_out_button = QPushButton("Zoom Out", self)
        self.zoom_out_button.setToolTip("Zoom out of the graph")
        self.zoom_out_button.clicked.connect(self.zoom_out_graph)
        graph_controls_layout.addWidget(self.zoom_out_button)

        graph_layout.addLayout(graph_controls_layout)

        self.graph_display = QLabel("Graph will be displayed here after simulation.", self)
        self.graph_display.setAlignment(Qt.AlignCenter)
        graph_layout.addWidget(self.graph_display)
        graph_tab.setLayout(graph_layout)
        tabs.addTab(graph_tab, "Graphs")

        # Logs Tab
        logs_tab = QWidget()
        logs_layout = QVBoxLayout()
        self.logs_display = QTextEdit(self)
        self.logs_display.setReadOnly(True)
        logs_layout.addWidget(self.logs_display)
        self.export_logs_button = QPushButton("Export Logs", self)
        self.export_logs_button.setToolTip("Export logs to a file")
        self.export_logs_button.clicked.connect(self.export_logs)
        logs_layout.addWidget(self.export_logs_button)
        logs_tab.setLayout(logs_layout)
        tabs.addTab(logs_tab, "Logs")

        # Units and measurement settings
        self.unit_combo = QComboBox(self)
        self.unit_combo.addItems(["Metric (SI)", "Imperial"])
        settings_layout.addWidget(QLabel("Units:"))
        settings_layout.addWidget(self.unit_combo)
        self.thrust_unit_combo = QComboBox(self)
        self.thrust_unit_combo.addItems(["Newtons (N)", "Kilograms-force (kgf)", "Pounds-force (lbf)"])
        settings_layout.addWidget(QLabel("Thrust Units:"))
        settings_layout.addWidget(self.thrust_unit_combo)

        # Time step control
        self.time_step_slider = QSlider(Qt.Horizontal, self)
        self.time_step_slider.setRange(1, 100)
        self.time_step_slider.setValue(10)
        self.time_step_slider.setTickInterval(1)
        self.time_step_slider.setTickPosition(QSlider.TicksBelow)
        settings_layout.addWidget(QLabel("Time Step:"))
        settings_layout.addWidget(self.time_step_slider)

        # Additional parameter settings
        self.wind_speed_slider = QSlider(Qt.Horizontal, self)
        self.wind_speed_slider.setRange(0, 100)
        self.wind_speed_slider.setValue(5)
        self.wind_speed_slider.setTickInterval(5)
        self.wind_speed_slider.setTickPosition(QSlider.TicksBelow)
        settings_layout.addWidget(QLabel("Wind Speed (m/s):"))
        settings_layout.addWidget(self.wind_speed_slider)

        self.temperature_slider = QSlider(Qt.Horizontal, self)
        self.temperature_slider.setRange(-50, 50)
        self.temperature_slider.setValue(20)
        self.temperature_slider.setTickInterval(5)
        self.temperature_slider.setTickPosition(QSlider.TicksBelow)
        settings_layout.addWidget(QLabel("Temperature (°C):"))
        settings_layout.addWidget(self.temperature_slider)

        self.humidity_slider = QSlider(Qt.Horizontal, self)
        self.humidity_slider.setRange(0, 100)
        self.humidity_slider.setValue(50)
        self.humidity_slider.setTickInterval(10)
        self.humidity_slider.setTickPosition(QSlider.TicksBelow)
        settings_layout.addWidget(QLabel("Humidity (%):"))
        settings_layout.addWidget(self.humidity_slider)

        # Reset settings button
        self.reset_button = QPushButton("Reset to Default", self)
        self.reset_button.clicked.connect(self.reset_to_default)
        settings_layout.addWidget(self.reset_button)

        # Add a button for text-to-speech
        self.tts_button = QPushButton("Read Simulation Data", self)
        self.tts_button.clicked.connect(self.read_simulation_data)
        settings_layout.addWidget(self.tts_button)

        settings_tab.setLayout(settings_layout)
        tabs.addTab(settings_tab, "Settings")

        self.setLayout(main_layout)
        self.show()

    # def Visualize_3D_Model(self):
    #     # This function will trigger the 3D model rendering in the OpenGL widget
    #     self.opengl_widget.update()

    # def load_3d_model(self):
    #     options = QFileDialog.Options()
    #     file_name, _ = QFileDialog.getOpenFileName(self, "Open 3D Model", "", "3D Files (*.obj);;All Files (*)", options=options)
    #     if file_name:
    #         self.opengl_widget.load_model(file_name)

    def load_3d_model_pyvista(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open 3D Model", "", "STL Files (*.stl);;OBJ Files (*.obj);;All Files (*)")
        if file_name:
            self.plotter = pv.Plotter(window_size=[800, 600])
            mesh = pv.read(file_name)
            self.plotter.add_mesh(mesh, color='white')
            self.plotter.add_axes()
            self.plotter.show()


    def set_black_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)

    def set_white_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, Qt.white)
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, Qt.white)
        palette.setColor(QPalette.AlternateBase, Qt.white)
        palette.setColor(QPalette.ToolTipBase, Qt.black)
        palette.setColor(QPalette.ToolTipText, Qt.black)
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.Button, Qt.white)
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)

    def set_system_theme(self):
        self.setPalette(self.style().standardPalette())

    def set_font_size(self):
        font, ok = QFontDialog.getFont(self.font(), self, "Select Font Size")
        if ok:
            self.setFont(font)

    def set_font_style(self):
        font, ok = QFontDialog.getFont(self.font(), self, "Select Font Style")
        if ok:
            self.setFont(font)

    def save_configuration(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Configuration", "", "JSON Files (*.json)", options=options)
        if file_name:
            config = {param: self.inputs[param].text() for param in self.inputs}
            with open(file_name, 'w') as file:
                json.dump(config, file)

    def load_configuration(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Configuration", "", "JSON Files (*.json)", options=options)
        if file_name:
            with open(file_name, 'r') as file:
                config = json.load(file)
                for param in self.inputs:
                    self.inputs[param].setText(config.get(param, ""))

    def toggle_data_logging(self):
        # Toggle data logging feature
        pass

    def run_simulation(self):
        if self.simulation_running:
            return  # Prevent multiple simulations from running simultaneously

        try:
            Thrust = self.convert_thrust(float(self.inputs["Thrust (N)"].text()))
            G = float(self.inputs["Gravity (m/s^2)"].text())
            dry_mass = float(self.inputs["Dry Mass (kg)"].text())
            wet_mass = float(self.inputs["Wet Mass (kg)"].text())
            length = float(self.inputs["Length (m)"].text())
            diameter = float(self.inputs["Diameter (m)"].text())
            material = self.inputs["Material"].text()
            specific_impulse = float(self.inputs["Specific Impulse (s)"].text())
            launch_angle = float(self.inputs["Launch Angle (degrees)"].text())
            avionics_weight = float(self.inputs["Avionics Weight (kg)"].text())
            initial_velocity = float(self.inputs["Initial Velocity (m/s)"].text())
            initial_acceleration = float(self.inputs["Initial Acceleration (m/s^2)"].text())
            drag_coefficient = float(self.inputs["Drag Coefficient (Cd)"].text())
            atmospheric_density = float(self.inputs["Atmospheric Density (kg/m^3)"].text())
            fuel_burn_rate = float(self.inputs["Fuel Burn Rate (kg/s)"].text())
            wind_speed = self.wind_speed_slider.value()
            temperature = self.temperature_slider.value()
            humidity = self.humidity_slider.value()
        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please enter valid numerical values")
            return

        self.simulation_running = True
        self.simulation_paused = False
        self.progress_bar.setVisible(True)
        self.speed = self.speed_slider.value()
        self.time_elapsed = 0
        self.dt = self.time_step_slider.value() / 100  # Convert to fractional time step
        self.time_steps = int(200 / self.dt)
        self.positions = np.zeros((self.time_steps, 3))
        self.velocities = np.zeros((self.time_steps, 3))
        self.accelerations = np.zeros((self.time_steps, 3))
        self.current_step = 0

        self.simulation_params = {
            'Thrust': Thrust,
            'G': G,
            'dry_mass': dry_mass,
            'wet_mass': wet_mass,
            'length': length,
            'diameter': diameter,
            'material': material,
            'specific_impulse': specific_impulse,
            'launch_angle': launch_angle,
            'avionics_weight': avionics_weight,
            'initial_velocity': initial_velocity,
            'initial_acceleration': initial_acceleration,
            'drag_coefficient': drag_coefficient,
            'atmospheric_density': atmospheric_density,
            'fuel_burn_rate': fuel_burn_rate,
            'wind_speed': wind_speed,
            'temperature': temperature,
            'humidity': humidity
        }

        self.timer.start(1000 // self.speed)

    def convert_thrust(self, value):
        unit = self.thrust_unit_combo.currentText()
        if unit == "Kilograms-force (kgf)":
            return value * 9.80665
        elif unit == "Pounds-force (lbf)":
            return value * 4.44822
        return value  # Default is Newtons

    def update_simulation(self):
        if not self.simulation_running or self.simulation_paused:
            return

        if self.current_step >= self.time_steps:
            self.timer.stop()
            self.simulation_running = False
            self.progress_bar.setVisible(False)
            self.display_results()
            return

        # Update simulation logic
        self.positions[self.current_step], self.velocities[self.current_step], self.accelerations[self.current_step] = self.simulate_step(self.current_step * self.dt)
        self.current_step += 1

        progress = int((self.current_step / self.time_steps) * 100)
        self.progress_bar.setValue(progress)

        if self.real_time_checkbox.isChecked():
            self.update_graph()

    def simulate_step(self, t):
        def thrust_force(t):
            return self.simulation_params['Thrust'] if t <= self.simulation_params['specific_impulse'] else 0

        def drag_force(v):
            Cd = self.simulation_params['drag_coefficient']
            A = np.pi * (self.simulation_params['diameter'] / 2)**2
            rho = self.simulation_params['atmospheric_density']
            if np.linalg.norm(v) == 0:
                return np.array([0.0, 0.0, 0.0])
            return 0.5 * Cd * A * rho * np.linalg.norm(v) ** 2 * -v / np.linalg.norm(v)

        def mass(t):
            burn_rate = self.simulation_params['fuel_burn_rate']
            if t <= self.simulation_params['specific_impulse']:
                return self.simulation_params['wet_mass'] - burn_rate * t
            else:
                return self.simulation_params['dry_mass']

        v = np.array([0.0, 0.0, self.simulation_params['initial_velocity']])
        r = np.array([0.0, 0.0, 0.0])
        angle = np.radians(self.simulation_params['launch_angle'])
        thrust_direction = np.array([np.cos(angle), 0, np.sin(angle)])

        def rk4_step(f, y, t, dt):
            k1 = f(y, t)
            k2 = f(y + 0.5 * dt * k1, t + 0.5 * dt)
            k3 = f(y + 0.5 * dt * k2, t + 0.5 * dt)
            k4 = f(y + dt * k3, t + dt)
            return y + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

        def derivatives(y, t):
            r, v = y[:3], y[3:]
            m = mass(t)
            F_thrust = thrust_force(t) * thrust_direction
            F_drag = drag_force(v)
            F_gravity = np.array([0, 0, -m * self.simulation_params['G']])
            F_net = F_thrust + F_drag + F_gravity
            a = F_net / m
            return np.concatenate((v, a))

        y = np.concatenate((r, v))
        y_next = rk4_step(derivatives, y, t, self.dt)
        return y_next[:3], y_next[3:], derivatives(y_next, t)[3:]

    def update_graph(self):
        # Code to update the graph in real-time
        pass

    def save_graph(self):
        # Implement saving graph functionality
        pass

    def zoom_in_graph(self):
        # Implement zoom in functionality for graphs
        pass

    def zoom_out_graph(self):
        # Implement zoom out functionality for graphs
        pass

    def export_logs(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Logs", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'w') as file:
                file.write(self.logs_display.toPlainText())

    def pause_simulation(self):
        if self.simulation_running:
            self.simulation_paused = not self.simulation_paused

    def stop_simulation(self):
        self.timer.stop()
        self.simulation_running = False
        self.simulation_paused = False
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.current_step = 0
        # Clear data or reset UI elements if necessary

    def display_results(self):
        # Display the results after the simulation
        graph_type = self.graph_type_combo.currentText()
        simulate_rocket(self.simulation_params, self.positions, self.velocities, self.accelerations, graph_type)

    def reset_to_default(self):
        # Reset all settings and configurations to their default values
        self.unit_combo.setCurrentIndex(0)
        self.thrust_unit_combo.setCurrentIndex(0)
        self.time_step_slider.setValue(10)
        self.wind_speed_slider.setValue(5)
        self.temperature_slider.setValue(20)
        self.humidity_slider.setValue(50)
        self.set_black_theme()

    def read_simulation_data(self):
        # Construct and read simulation data using TTS
        altitude = self.positions[self.current_step - 1][2]
        velocity = np.linalg.norm(self.velocities[self.current_step - 1])
        acceleration = np.linalg.norm(self.accelerations[self.current_step - 1])
        trajectory_info = f"Current altitude: {altitude:.2f} meters, Velocity: {velocity:.2f} meters per second, Acceleration: {acceleration:.2f} meters per second squared."
        self.tts_engine.say(trajectory_info)
        self.tts_engine.runAndWait()


# class OpenGLWidget(QGLWidget):
    # def __init__(self, parent=None):
    #     super().__init__(parent)
    #     self.model = None

    # def load_model(self, file_name):
    #     self.model = self.load_obj(file_name)
    #     self.update()

    # def load_obj(self, filename):
    #     vertices = []
    #     faces = []
    #     with open(filename, 'r') as file:
    #         for line in file:
    #             if line.startswith('v '):
    #                 vertices.append(list(map(float, line.strip().split()[1:4])))
    #             elif line.startswith('f '):
    #                 faces.append([int(idx.split('/')[0]) - 1 for idx in line.strip().split()[1:]])
    #     return {'vertices': vertices, 'faces': faces}

    # def initializeGL(self):
    #     glClearColor(0.0, 0.0, 0.0, 1.0)
    #     glEnable(GL_DEPTH_TEST)

    # def resizeGL(self, w, h):
    #     if h == 0:
    #         h = 1 # prevent division by zero 
            
    #     glViewport(0, 0, w, h)
    #     glMatrixMode(GL_PROJECTION)
    #     glLoadIdentity()
    #     gluPerspective(45, w / h, 0.1, 100.0)
    #     glMatrixMode(GL_MODELVIEW)

    # def paintGL(self):
    #     glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    #     glLoadIdentity()
    #     glTranslatef(0.0, 0.0, -5.0)
    #     if self.model:
    #         self.draw_model()

    # def draw_model(self):
    #     glBegin(GL_TRIANGLES)
    #     for face in self.model['faces']:
    #         for vertex_idx in face:
    #             glVertex3fv(self.model['vertices'][vertex_idx])
    #     glEnd()


def simulate_rocket(params, positions, velocities, accelerations, graph_type):
    # This function should use the data collected during the simulation to display the results
    time = np.arange(len(positions)) * 0.1  # Example time array

    if graph_type == "3D Trajectory":
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(positions[:, 0], positions[:, 1], positions[:, 2])
        ax.set_title('3D Rocket Trajectory')
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
    elif graph_type == "Altitude vs Time":
        plt.figure(figsize=(10, 8))
        plt.plot(time, positions[:, 2])
        plt.title('Altitude vs Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Altitude (m)')
    elif graph_type == "Velocity vs Time":
        plt.figure(figsize=(10, 8))
        plt.plot(time, np.linalg.norm(velocities, axis=1))
        plt.title('Velocity vs Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Velocity (m/s)')
    elif graph_type == "Acceleration vs Time":
        plt.figure(figsize=(10, 8))
        plt.plot(time, np.linalg.norm(accelerations, axis=1))
        plt.title('Acceleration vs Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Acceleration (m/s^2)')

    plt.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RocketSimulator()
    sys.exit(app.exec_())
