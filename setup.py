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

        # The executable path is simply the name of the script, as it will be in the PATH
        exe_path = 'delayed-shutdown'

        # It's not straightforward to get the icon path reliably after installation.
        # A common approach is to place it in a standard location or to use a post-install script
        # that knows about the package structure.
        # For pipx, the package is installed in an isolated environment.
        # We'll assume the icon is located relative to the package.
        # A better long-term solution might be to use `pkg_resources` or `importlib.resources`.
        # For now, this dynamic path finding should be more reliable.

        # We need to find where the package is installed to locate the icon.
        # A simple way is to import the package and check its __file__ attribute.
        # This part of the script runs *after* the package has been installed.
        import delayed_shutdown
        package_path = os.path.dirname(delayed_shutdown.__file__)
        icon_path = os.path.join(package_path, 'ui', 'images', 'icon.png')

        desktop_entry = f"""\
[Desktop Entry]
Version=1.0
Type=Application
Name=Delayed Shutdown
Comment=Shutdown computer after specified processes finish
Exec={exe_path}
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
