from sys import platform
from connector import Connector


if __name__ == '__main__':
    if platform.startswith("win"):
        nwconnector = Connector()
        nwconnector.run()
    else:
        raise NotImplementedError(
            f"Current tools is based netsh - a Windows "
            f"tool you are running it on {platform}"
        )