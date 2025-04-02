import serial
import serial.tools.list_ports
import pandas as pd
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets  
import signal

# Function to list available USB ports
def get_available_ports():
    ports = serial.tools.list_ports.comports()
    return [(port.device, port.description) for port in ports]

# Function to refresh the list of available USB ports
def refresh_usb_ports():
    global port_dropdown
    current_ports = set(port_dropdown.itemData(i) for i in range(port_dropdown.count()))
    available_ports = get_available_ports()

    # Add new ports to the top of the dropdown
    for port, description in available_ports:
        if port not in current_ports:
            port_dropdown.insertItem(0, f"{port} - {description}", port)  # Insert at the top

    # Remove ports that are no longer available
    for i in range(port_dropdown.count() - 1, -1, -1):
        if port_dropdown.itemData(i) not in [port for port, _ in available_ports]:
            port_dropdown.removeItem(i)

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

# Update the plot function to plot all data
def update_plot():
    global curve_pdiff_mid, curve_pdiff_NS, curve_pdiff_EW, curve_speed
    df = update_data()

    # Check if the DataFrame is empty
    if df.empty:
        print("No data available to plot.")
        return

    # Use the entire DataFrame for plotting
    x = range(len(df))  # Generate x-axis values for all rows

    # Update the plots with all data
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
    # Disable Reset and Save buttons while the timer is running
    reset_button.setEnabled(False)
    save_button.setEnabled(False)

def stop_animation():
    timer.stop()
    # Enable Reset and Save buttons when the timer is stopped
    reset_button.setEnabled(True)
    save_button.setEnabled(True)

# Add a reset function
def reset_data():
    global df    
    # Clear the DataFrame
    df = pd.DataFrame(columns=data_fields)
    print("DataFrame has been reset.")
    
    # Clear the graph by resetting the data for all curves
    curve_pdiff_mid.setData([], [])
    curve_pdiff_NS.setData([], [])
    curve_pdiff_EW.setData([], [])
    curve_speed.setData([], [])
    print("Graph has been reset.")

# Add a save function
def save_data():
    global df
    options = QtWidgets.QFileDialog.Options()
    file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
        None, "Save DataFrame as CSV", "", "CSV Files (*.csv);;All Files (*)", options=options
    )
    if file_path:  # If the user selected a file
        df.to_csv(file_path, index=False)
        print(f"DataFrame saved to {file_path}")

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
button_layout.addWidget(save_button) 
layout.addLayout(button_layout)

plot_widget = pg.GraphicsLayoutWidget(show=True, title="Solano Visualizer")
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

# Initialize a QTimer to refresh USB ports periodically
usb_refresh_timer = QtCore.QTimer()
usb_refresh_timer.timeout.connect(refresh_usb_ports)
usb_refresh_timer.start(1000)  # Refresh every 1 second

# Connect buttons to functions 
start_button.clicked.connect(start_animation)
stop_button.clicked.connect(stop_animation)
reset_button.clicked.connect(reset_data)
save_button.clicked.connect(save_data)

# Gracefully close the application on Ctrl+C
def handle_sigint(signal, frame):
    print("Exiting application...")
    QtWidgets.QApplication.quit()

# Connect the SIGINT signal to the handler
signal.signal(signal.SIGINT, handle_sigint)

win.show()

# Start Qt event loop
QtWidgets.QApplication.instance().exec_()
