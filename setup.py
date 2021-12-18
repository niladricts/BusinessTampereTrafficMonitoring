from setuptools import find_packages
from setuptools import setup

setup(
    name="BusinessTampereTrafficMonitoring",
    version="0.0.1",
    url="https://github.com/niladricts/BusinessTampereTrafficMonitoring",
    install_requires=[
        "iotticket@git+https://github.com/IoT-Ticket/IoTTicket-PythonLibrary@06330351ac874b93dfcd7784910c4b8c7d95be83",
        "httpx",
        "numpy",
        "opencv-python",
        "Pillow",
        "respx",
        "SQLAlchemy",
        "tensorflow",
        "tf2-yolov4",
    ],
    packages=find_packages()
)
