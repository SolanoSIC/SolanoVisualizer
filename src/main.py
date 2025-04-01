import serial
import pandas as pd
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets  

# Initialize USB connection
usb_port = 'COM4'  # Change this to your USB port
baud_rate = 230400
ser = serial.Serial(usb_port, baud_rate)

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
    global df
    while ser.in_waiting > 0:  # Read all available data
        line_data = ser.readline().decode('utf-8').strip()
        try:
            values = list(map(float, line_data.split(';')))
            if len(values) == len(data_fields):
                new_row = pd.DataFrame([values], columns=data_fields)
                df = pd.concat([df, new_row], ignore_index=True)
                # print(f"DataFrame updated:\n{df.tail()}")  # Debugging print statement
        except ValueError:
            print("Error parsing data")  # Debugging print statement
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

# Initialize PyQtGraph
app = QtWidgets.QApplication([])  
win = QtWidgets.QWidget()
layout = QtWidgets.QVBoxLayout()
win.setLayout(layout)

# Buttons settings and layout
button_layout = QtWidgets.QHBoxLayout()
start_button = QtWidgets.QPushButton("Start")
stop_button = QtWidgets.QPushButton("Stop")
button_layout.addWidget(start_button)
button_layout.addWidget(stop_button)
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

start_button.clicked.connect(start_animation)
stop_button.clicked.connect(stop_animation)

win.show()

# Start Qt event loop
QtWidgets.QApplication.instance().exec_()
