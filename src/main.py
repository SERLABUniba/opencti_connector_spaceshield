import traceback
from connector.connector import SpaceShieldConnector
from connector.settings import ConnectorSettings
from pycti import OpenCTIConnectorHelper

if __name__ == "__main__":
    """
    The Entry point of the connector
    """
    try:
        settings = ConnectorSettings()
        helper = OpenCTIConnectorHelper(config=settings.to_helper_config())
        connector = SpaceShieldConnector(config=settings, helper=helper)
        connector.run()
    except Exception:
        traceback.print_exc()
        exit(1)