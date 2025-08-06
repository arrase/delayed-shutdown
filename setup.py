from setuptools import setup, find_packages

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
)
