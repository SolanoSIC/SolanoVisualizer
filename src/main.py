import serial
import serial.tools.list_ports
import pandas as pd
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets  

# Function to list available USB ports
def get_available_ports():
    ports = serial.tools.list_ports.comports()
    return [(port.device, port.description) for port in ports]

# Initialize USB connection (default values)
usb_port = None
baud_rate = 230400
ser = None

# Prepare data storage
data_fields = [
    "Speed", "Speed_filtered", "Speed_corrected", "pdiff_mid", "pdiff_NS", "pdiff_EW",
    "pdiff_mid_filtered", "pdiff_NS_filtered", "pdiff_EW_filtered", "angle_NS", "angle_EW",
    "angle_NS_filtered", "angle_EW_filtered", "temp_mid", "temp_NS", "temp_EW"
]

# Initialize DataFrame
df = pd.DataFrame(columns=data_fields)

# Read data from USB port and concat to DataFrame
def update_data():
    global df, ser
    if ser and ser.in_waiting > 0:  # Read all available data
        line_data = ser.readline().decode('utf-8').strip()
        try:
            values = list(map(float, line_data.split(';')))
            if len(values) == len(data_fields):
                new_row = pd.DataFrame([values], columns=data_fields)
                df = pd.concat([df, new_row], ignore_index=True)
        except ValueError:
            print("Error parsing data")
    return df

def update_plot():
    global curve_pdiff_mid, curve_pdiff_NS, curve_pdiff_EW, curve_speed
    df = update_data()
    x = range(len(df))
    
    y1 = df['pdiff_mid']
    curve_pdiff_mid.setData(x, y1)
    
    y2 = df['pdiff_NS']
    curve_pdiff_NS.setData(x, y2)
    
    y3 = df['pdiff_EW']
    curve_pdiff_EW.setData(x, y3)
    
    y4 = df['Speed']
    curve_speed.setData(x, y4)

timer = QtCore.QTimer()
timer.timeout.connect(update_plot)

def start_animation():
    timer.start(5)

def stop_animation():
    timer.stop()

# Add a reset function
def reset_data():
    global df
    if not timer.isActive():  # Check if the program is not running
        df = pd.DataFrame(columns=data_fields)  # Clear the DataFrame
        print("DataFrame has been reset.")
    else:
        print("Cannot reset while the program is running.")

# Add a save function
def save_data():
    global df
    if not timer.isActive():  # Check if the program is not running
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            None, "Save DataFrame as CSV", "", "CSV Files (*.csv);;All Files (*)", options=options
        )
        if file_path:  # If the user selected a file
            df.to_csv(file_path, index=False)
            print(f"DataFrame saved to {file_path}")
    else:
        print("Cannot save while the program is running.")

# Function to update the selected USB port
def update_usb_port(index):
    global ser, usb_port
    selected_port = port_dropdown.itemData(index)
    if selected_port:
        usb_port = selected_port
        if ser:
            ser.close()
        try:
            ser = serial.Serial(usb_port, baud_rate)
            print(f"Connected to: {usb_port}")
        except serial.SerialException as e:
            print(f"Failed to connect to {usb_port}: {e}")

# Initialize PyQtGraph
app = QtWidgets.QApplication([])  
win = QtWidgets.QWidget()
layout = QtWidgets.QVBoxLayout()
win.setLayout(layout)

# Dropdown menu for USB ports
port_dropdown = QtWidgets.QComboBox()
available_ports = get_available_ports()
for port, description in available_ports:
    port_dropdown.addItem(f"{port} - {description}", port)
port_dropdown.currentIndexChanged.connect(update_usb_port)
layout.addWidget(port_dropdown)

# Buttons settings and layout
button_layout = QtWidgets.QHBoxLayout()
start_button = QtWidgets.QPushButton("Start")
stop_button = QtWidgets.QPushButton("Stop")
reset_button = QtWidgets.QPushButton("Reset")  
save_button = QtWidgets.QPushButton("Save")

button_layout.addWidget(start_button)
button_layout.addWidget(stop_button)
button_layout.addWidget(reset_button)  
button_layout.addWidget(save_button)  # Add the Save button to the same layout as the others
layout.addLayout(button_layout)



plot_widget = pg.GraphicsLayoutWidget(show=True, title="USB Data Visualizer")
plot_widget.resize(1000, 600)

# First plot for pdiff values
plot1 = plot_widget.addPlot(title="pdiff values")
curve_pdiff_mid = plot1.plot(pen='y', name="pdiff_mid")
curve_pdiff_NS = plot1.plot(pen='r', name="pdiff_NS")
curve_pdiff_EW = plot1.plot(pen='b', name="pdiff_EW")

# Add a new row for the second plot
plot_widget.nextRow()

# Second plot for speed
plot2 = plot_widget.addPlot(title="Speed")
curve_speed = plot2.plot(pen='g', name="Speed")

layout.addWidget(plot_widget)


# Connect buttons to functions 
start_button.clicked.connect(start_animation)
stop_button.clicked.connect(stop_animation)
reset_button.clicked.connect(reset_data)
save_button.clicked.connect(save_data)
win.show()

# Start Qt event loop
QtWidgets.QApplication.instance().exec_()
