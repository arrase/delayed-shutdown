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

## Configuration

### Run Shutdown Without a Password

To allow the application to shut down the system without asking for a password, you need to configure `sudo`. This allows the `shutdown` command to be executed without user interaction.

**Warning:** Editing the `sudoers` file incorrectly can leave your system in an unstable state. Proceed with caution.

1.  **Find the `shutdown` command path:**
    Open a terminal and run:
    ```bash
    which shutdown
    ```
    This will give you the full path to the command, for example, `/usr/sbin/shutdown`. Copy it.

2.  **Edit the `sudoers` file:**
    The safest way to edit this file is with the `visudo` command, which checks the syntax before saving.
    ```bash
    sudo visudo
    ```

3.  **Add the rule:**
    Add the following line to the end of the file. **Important:** Replace `<YOUR USER>` with your username and `<PATH TO SHUTDOWN>` with the path you copied in the first step.

    ```
    <YOUR USER> ALL=(ALL) NOPASSWD: <PATH TO SHUTDOWN>
    ```

    For example, if your user is `john` and the path is `/usr/sbin/shutdown`, the line would be:
    `john ALL=(ALL) NOPASSWD: /usr/sbin/shutdown`

4.  **Save and exit.** In `visudo` (which typically uses an editor like `vi` or `nano`), save the changes and exit. If you're using `vi`, press `Esc` and type `:wq`. If you're using `nano`, press `Ctrl+X`, then `Y`, and `Enter`.

## Desktop Integration

To make the application appear in your desktop environment's application menu, you can create a `.desktop` file.

### For KDE Plasma (and other Linux Desktops)

1.  **Find the executable path:**
    First, find where `pipx` installed the application. Open a terminal and run:
    ```bash
    which delayed-shutdown
    ```
    This will output the full path, for example: `/home/<YOUR USER HERE>/.local/bin/delayed-shutdown`. Copy this path.

2.  **Create the `.desktop` file:**
    Create a new file in your local applications directory using your favorite text editor (e.g., `kate`, `nano`, `gedit`):
    ```bash
    vim ~/.local/share/applications/delayed-shutdown.desktop
    ```

3.  **Add the following content:**
    Paste the text below into the file. **Important:** Replace the path in the `Exec=` line with the one you copied in the first step.

    ```ini
    [Desktop Entry]
    Version=1.0
    Type=Application
    Name=Delayed Shutdown
    Comment=Shutdown computer after specified processes finish
    Exec=/home/<YOUR USER HERE>/.local/bin/delayed-shutdown
    Icon=system-shutdown
    Terminal=false
    Categories=System;Utility;
    ```

4.  **Save and close the file.** The application should now appear in your application menu. If it doesn't show up immediately, you may need to log out and log back in.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or find any bugs.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
