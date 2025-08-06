import os
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        self.create_desktop_entry()

    def create_desktop_entry(self):
        """Creates the .desktop file for the application."""
        if sys.platform != 'linux':
            print("Skipping .desktop file creation on non-linux platform")
            return

        # self.install_lib is the directory where the package is installed.
        # This ensures we have the final, absolute paths after installation.
        icon_path = os.path.abspath(os.path.join(
            self.install_lib, 'delayed_shutdown', 'ui', 'images', 'icon.png'
        ))

        desktop_entry = f"""
[Desktop Entry]
Version=1.0
Type=Application
Name=Delayed Shutdown
Comment=Shutdown computer after specified processes finish
Exec=delayed-shutdown
Icon={icon_path}
Terminal=false
Categories=System;Utility;
"""

        app_dir = os.path.join(os.path.expanduser('~'), '.local', 'share', 'applications')
        os.makedirs(app_dir, exist_ok=True)
        desktop_file_path = os.path.join(app_dir, 'delayed-shutdown.desktop')

        with open(desktop_file_path, 'w') as f:
            f.write(desktop_entry)

        print(f"Created desktop entry at {desktop_file_path}")

setup(
    name="delayed-shutdown",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "psutil",
        "PyQt6",
    ],
    entry_points={
        "console_scripts": [
            "delayed-shutdown=delayed_shutdown.__main__:main",
        ],
    },
    author="Juan Ezquerro LLanes",
    author_email="arrase@gmail.com",
    description="A GUI application to shut down the computer after specified processes have finished.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/arrase/delayed-shutdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True,
    cmdclass={
        'install': PostInstallCommand,
    },
)
