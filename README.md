# SolanoVisualizer

SolanoVisualizer is a Python-based application that visualizes data from a USB device in real-time using PyQtGraph. It allows users to connect to a USB port, visualize data, and saving them as a CSV file.

## Features

### 1. **USB Port Selection**
- The application automatically detects available USB ports on your computer.
- A dropdown menu allows you to select the desired USB port to connect to.
- The selected port is used to establish a connection with the USB device.

### 2. **Real-Time Data Visualization**
- Data from the USB device is read and visualized in real-time.
- Two plots are displayed:
  - **pdiff values**: Displays `pdiff_mid`, `pdiff_NS`, and `pdiff_EW`.
  - **Speed**: Displays the `Speed` data.

### 3. **Start and Stop Buttons**
- **Start**: Begins the real-time data visualization.
- **Stop**: Pauses the data visualization.

### 4. **Reset Button**
- Clears the DataFrame containing the collected data.
- **Note**: The reset operation is only allowed when the program is not running (i.e., when the visualization is stopped).

### 5. **Save Button**
- Allows you to save the collected data to a CSV file.
- Opens a file dialog to let you choose the file name and location.
- **Note**: Saving is only allowed when the program is not running.

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

## Requirements

- Python 3.x
- Required libraries:
  - `pyqtgraph`
  - `pandas`
  - `pyserial`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/SolanoVisualizer.git
   cd SolanoVisualizer
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Use

1. **Select a USB Port**:
   - Use the dropdown menu to select the USB port connected to your device.

2. **Start Visualization**:
   - Click the "Start" button to begin visualizing data in real-time.

3. **Stop Visualization**:
   - Click the "Stop" button to pause the visualization.

4. **Reset Data**:
   - Click the "Reset" button to clear the collected data.
   - Ensure the program is stopped before resetting.

5. **Save Data**:
   - Click the "Save" button to save the collected data to a CSV file.
   - Choose the file name and location in the dialog that appears.
   - Ensure the program is stopped before saving.

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.
