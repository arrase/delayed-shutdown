# Delayed Shutdown

A simple GUI application to shut down your computer after a set of specified processes have finished executing.

![Application Screenshot](image.png)

## Features

- **Process Monitoring:** Select one or more running processes to monitor.
- **Automatic Shutdown:** The application will automatically shut down the computer once all monitored processes have finished.
- **Customizable Interval:** Set the monitoring interval to check if the processes have finished.
- **Shutdown Countdown:** A 30-second countdown is initiated before shutting down, which can be canceled.

## Installation

### From a public GitHub repository (recommended)

You can install the application using `pipx` from the public GitHub repository:

```bash
pipx install git+https://github.com/arrase/delayed-shutdown.git
```

### From local directory

To install the application, clone the repository and run the following command in the project's root directory:

```bash
pip install .
```

## Usage

After installation, you can run the application from your terminal:

```bash
delayed-shutdown
```

This will open a window where you can select the processes to monitor. Once you've selected the desired processes, click "Start Monitoring and Shutdown". The application will wait for all selected processes to close and then initiate a 30-second countdown to shut down your computer.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or find any bugs.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
