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

# Initialize PyQtGraph
app = QtWidgets.QApplication([])  # Create the QApplication instance first

# Initialize the main window and layout
win = QtWidgets.QWidget()
layout = QtWidgets.QVBoxLayout()
# Create a widget for the checkboxes
checkbox_widget = QtWidgets.QWidget()
checkbox_layout = QtWidgets.QVBoxLayout()
checkbox_widget.setLayout(checkbox_layout)


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

# Function to update plots dynamically based on selected categories
def update_plot():
    global df, dynamic_plots
    df = update_data()

    # Get the selected time window in seconds
    time_window_seconds = time_window_spinbox.value()
    points_to_display = time_window_seconds * 100  # Calculate the number of points to display

    # Use the tail function to get the last `points_to_display` rows
    filtered_df = df.tail(points_to_display)
    filtered_df = filtered_df.reset_index(drop=True)

    # Check if the filtered DataFrame is empty
    if filtered_df.empty:
        print("No data available to plot.")
        return

    # Use the index of the filtered DataFrame for the x-axis
    x = range(len(filtered_df))

    # Get the selected categories from the checkboxes
    selected_categories = [category for category, checkbox in category_checkboxes.items() if checkbox.isChecked()]

    # Clear existing plots and recreate them
    for category in selected_categories:
        if category not in dynamic_plots:
            # Create a new plot for this category
            plot = plot_widget.addPlot(title=category)
            dynamic_plots[category] = plot
            plot_widget.nextRow()  # Add the next plot in a new row

        # Update the plot with the filtered data for all fields in the category
        plot = dynamic_plots[category]
        plot.clear()  # Clear the plot before re-adding data
        fields_to_plot = field_mapping.get(category, [])
        for field in fields_to_plot:
            if field in filtered_df.columns:
                color = color_mapping.get(field, (0, 0, 0))  # Default to black if no color is defined
                plot.plot(x, filtered_df[field], pen=pg.mkPen(color=color, width=2), name=field)

    # Remove plots for categories that are no longer selected
    for category in list(dynamic_plots.keys()):
        if category not in selected_categories:
            plot = dynamic_plots.pop(category)
            plot_widget.removeItem(plot)


# Define the field mapping for categories
field_mapping = {
    "Speed": ["Speed"],
    "Speed filtered": ["Speed_filtered"],
    "Pdiff": ["pdiff_mid", "pdiff_NS", "pdiff_EW"],
    "Pdiff filtered": ["pdiff_mid_filtered", "pdiff_NS_filtered", "pdiff_EW_filtered"],
    "Angle": ["angle_NS", "angle_EW"],
    "Angle filtered": ["angle_NS_filtered", "angle_EW_filtered"],
    "Temp": ["temp_mid", "temp_NS", "temp_EW"]
}

# Define the color mapping for the plots
color_mapping = {
    "Speed": (0, 255, 0),  # Green
    "Speed_filtered": (0, 255, 0),  # Green
    "pdiff_mid": (255, 0, 0),  # Red
    "pdiff_NS": (0, 128, 255),  # Blue
    "pdiff_EW": (255, 255, 0),  # Yellow
    "pdiff_mid_filtered": (255, 0, 0),  # Red
    "pdiff_NS_filtered": (0, 128, 255),  # Blue
    "pdiff_EW_filtered": (255, 255, 0),  # Yellow
    "angle_NS": (0, 128, 255),  # Blue
    "angle_EW": (255, 255, 0),  # Yellow
    "angle_NS_filtered": (0, 128, 255),  # Blue
    "angle_EW_filtered": (255, 255, 0),  # Yellow
    "temp_mid": (255, 69, 0),  # Orange-Red
    "temp_NS": (0, 100, 0),  # Dark Green
    "temp_EW": (70, 130, 180)  # Steel Blue
}



# Dictionary to store checkboxes for each category
category_checkboxes = {}

# Create a checkbox for each category
for category in field_mapping.keys():
    checkbox = QtWidgets.QCheckBox(category)
    # Tick "Speed filtered" and "Angle filtered" by default
    if category in ["Speed filtered", "Angle filtered"]:
        checkbox.setChecked(True)
    checkbox.stateChanged.connect(update_plot)  # Connect state change to update_plot
    checkbox_layout.addWidget(checkbox)
    category_checkboxes[category] = checkbox

# Create the main layout
main_layout = QtWidgets.QHBoxLayout()

# Add the existing layout (left side) to the main layout
main_layout.addLayout(layout)

# Add the checkbox widget (right side) to the main layout
main_layout.addWidget(checkbox_widget)

# Set the main layout as the layout for the main window
win.setLayout(main_layout)

# Dictionary to store dynamically created plots
dynamic_plots = {}



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
    global df, dynamic_plots

    # Clear the DataFrame
    df = pd.DataFrame(columns=data_fields)

    # Clear all plots but keep the default graphs
    for category, plot in dynamic_plots.items():
        plot.clear()  # Clear the plot data but keep the plot itself
        fields_to_plot = field_mapping.get(category, [])
        for field in fields_to_plot:
            if field in data_fields:  # Ensure the field exists in the data_fields
                color = color_mapping.get(field, (0, 0, 0))  # Default to black if no color is defined
                plot.plot([], [], pen=pg.mkPen(color=color, width=2), name=field)

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

# Add a spinbox for selecting the time window
time_window_label = QtWidgets.QLabel("Time Window (seconds):")
time_window_spinbox = QtWidgets.QSpinBox()
time_window_spinbox.setRange(1, 60)  # Allow the user to select between 1 and 60 seconds
time_window_spinbox.setValue(5)  # Default to 10 seconds

# Add the spinbox to the layout
time_window_layout = QtWidgets.QHBoxLayout()
time_window_layout.addWidget(time_window_label)
time_window_layout.addWidget(time_window_spinbox)
layout.addLayout(time_window_layout)

plot_widget = pg.GraphicsLayoutWidget(show=True, title="Solano Visualizer")
plot_widget.resize(1000, 600)

# Add default plots for "Speed filtered" and "Angle filtered"
for category in ["Speed filtered", "Angle filtered"]:
    if category in field_mapping:
        # Create a new plot for this category
        plot = plot_widget.addPlot(title=category)
        dynamic_plots[category] = plot
        plot_widget.nextRow()  # Add the next plot in a new row

        # Populate the plot with empty data initially
        fields_to_plot = field_mapping.get(category, [])
        for field in fields_to_plot:
            if field in data_fields:  # Ensure the field exists in the data_fields
                color = color_mapping.get(field, (0, 0, 0))  # Default to black if no color is defined
                plot.plot([], [], pen=pg.mkPen(color=color, width=2), name=field)

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
