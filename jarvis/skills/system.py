import platform
import os


def system_status():
    return (
        "System: " + platform.system() + "\n"
        "Machine: " + platform.machine() + "\n"
        "Python: " + platform.python_version() + "\n"
        "PID: " + str(os.getpid())
    )
