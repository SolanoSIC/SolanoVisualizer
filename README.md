# USB Data Visualizer

This project is a Python application that reads data from a USB port and displays it on a real-time updating graph. It utilizes the `pyserial` library for serial communication and `pyqtgraph` for data visualization.

## Project Structure

```
SolanoVisualizer
├── src
│   ├── main.py          # Entry point of the application
│   └── utils
│       └── __init__.py  # Utility functions for data processing
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd SolanoVisualizer
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Connect your USB device to the computer.
2. Edit the `usb_port` variable in `src/main.py` to match your system's USB port:
   - **Windows**: Typically `COMx` where `x` is the port number (e.g., `COM4`).
   - **Linux**: Typically `/dev/ttyUSBx` or `/dev/ttyACMx` where `x` is the port number (e.g., `/dev/ttyUSB0`).

   Example for Windows:
   ```python
   usb_port = 'COM4'
   ```

   Example for Linux:
   ```python
   usb_port = '/dev/ttyUSB0'
   ```

3. Run the application:
   ```
   python src/main.py
   ```

4. The application will read data from the USB port and display it in real-time on a graph.

## Dependencies

- `pyserial`: For serial communication with the USB device.
- `pandas`: For data manipulation and analysis.
- `pyqtgraph`: For plotting the data in real-time.
- `pyqt5`: For the graphical user interface.

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.
