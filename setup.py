from setuptools import setup

setup(
    name="delayed-shutdown",
    version="0.1.0",
    py_modules=["main"],
    install_requires=[
        "psutil",
        "PyQt6",
    ],
    entry_points={
        "console_scripts": [
            "delayed-shutdown=main:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A GUI application to shut down the computer after specified processes have finished.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/delayed-shutdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True,
)
