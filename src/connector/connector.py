import json
from datetime import datetime, timezone
from typing import Optional

from pycti import OpenCTIConnectorHelper
from connector.settings import ConnectorSettings
from spaceshield_client import SpaceShieldClient


def _patched_initiate_work(self, connector_id: str, friendly_name: str, is_multipart: bool = False) -> Optional[str]:
    """
    This function query the database without the 'is_multipart'. 
    If you are using a version of OpenCTI <= 7.260428.0 use this method, otherwise comment it.

    :param connector_id: the connector id
    :param friendly_name: the friendly name for the work
    :param is_multipart: indicates whether multiple calls to `add_expectations`
                                are to be expected during the lifetime of the work.
                                In consequence the work won't automatically
                                transition to `complete` when the number of calls
                                to `report_expectation` matches the expectations
                                but only when an explicit call to `to_processed`
                                is made.
                                Should be set to `True` when sending multiple
                                STIX bundles consecutively via `send_stix2_bundle`
    :return: the id of the work added
    """

    query = """
        mutation WorkAdd($connectorId: String!, $friendlyName: String!) {
            workAdd(connectorId: $connectorId, friendlyName: $friendlyName) {
                id
            }
        }
    """
    work = self.api.query(query, {
        "connectorId": connector_id,
        "friendlyName": friendly_name,
    })
    return work["data"]["workAdd"]["id"]


class SpaceShieldConnector:
    def __init__(self, config: ConnectorSettings, helper: OpenCTIConnectorHelper):
        self.config = config
        self.helper = helper
        self.client = SpaceShieldClient(
            stix_url=config.spaceshield.stix_url
        )

        """
        The following code is useful to mutate the patched initiate work
        If you are using a version of OpenCTI <= 7.260428.0 use this method, otherwise comment it.
        """

        import types
        self.helper.api.work.initiate_work = types.MethodType(
            _patched_initiate_work, self.helper.api.work
        )

    def _run_once(self):
        """
        This function si useful to: 
            1) Download of the STIX Bundle from ESA, 
            2) Send the STIX Bundle to OpenCTI (updating the work status),
            3) Update the info related to import (i.e., "last_run")
        """

        work_id = None
        self.helper.log_info("Downloading the STIX bundle from SpaceShield by ESA...")
        try:
            work_id = self.helper.api.work.initiate_work(
                self.helper.connect_id,
                "SpaceShield ESA — importing TTPs"
            )
            self.helper.log_info(f"Work initiated with ID: {work_id}")

            bundle = self.client.get_stix_bundle()
            count = len(bundle.get("objects", []))
            self.helper.log_info(f"Received {count} STIX objects from SpaceShield.")

            self.helper.send_stix2_bundle(
                json.dumps(bundle),
                work_id=work_id,
                cleanup_inconsistent_bundle=True,
            )

            self.helper.set_state({
                "last_run": datetime.now(timezone.utc).isoformat(),
                "last_count": count,
            })

            self.helper.api.work.to_processed(
                work_id,
                f"SpaceShield ESA: successfully imported {count} STIX objects."
            )
            self.helper.log_info(f"Import completed successfully: {count} objects processed.")

        except Exception as e:
            self.helper.log_error(f"An unexpected error occurred during import: {e}")
            if work_id:
                self.helper.api.work.to_processed(
                    work_id,
                    f"Import failed with error: {str(e)}",
                    in_error=True,
                )
            raise

    def run(self):
        """
        This function run the connector's features
        """
        
        self.helper.log_info("Starting the SpaceShield ESA connector.")
        self.helper.schedule_iso(
            message_callback=self._run_once,
            duration_period=str(self.config.connector.duration_period),
        )