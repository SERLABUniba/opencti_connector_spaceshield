import requests

class SpaceShieldClient:
    def __init__(self, stix_url: str):
        self.stix_url = stix_url
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; OpenCTI-SpaceShield-Connector/1.0)",
            "Accept": "application/json",
        })

    def get_stix_bundle(self) -> dict:
        """
        This function download the complete STIX bundle from SpaceShield by ESA.
        :return: the json coresponding to the STIX Bundle
        """

        resp = self.session.get(self.stix_url, timeout=30)
        resp.raise_for_status()
        return resp.json()