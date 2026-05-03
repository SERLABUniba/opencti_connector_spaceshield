from datetime import timedelta

from connectors_sdk import (
    BaseConfigModel,
    BaseConnectorSettings,
    BaseExternalImportConnectorConfig,
    ListFromString
)
from pydantic import Field, HttpUrl

class ExternalImportConnectorConfig(BaseExternalImportConnectorConfig):
    #This field is for the ID of the Connector, the same in the .env file
    id: str = Field(
        description="A UUID v4 to identify the connector in OpenCTI.",
        default="eaf811a6-8cf0-4c50-92dc-338838332215",
    )

    scope: ListFromString = Field(
        description="The scope of the connector. Only these object types will be imported on OpenCTI.",
        default=[
            "identity",
            "attack-pattern",
            "course-of-action",
            "x-mitre-tactic",
            "x-mitre-matrix"
        ],
    )
    #This field is for the name of the connector
    name: str = Field(
        description="The name of the connector.",
        default="[C] SpaceShield ESA Connector",
    )
    #This field is for the delta time between to runs of the connector
    duration_period: timedelta = Field(
        description="The period of time to await between two runs of the connector.",
        default=timedelta(days=7),
    )

class SpaceShieldConfig(BaseConfigModel):
    #This field is for the URL of the json file
    stix_url: HttpUrl = Field(
        description="URL of the SPACE-SHIELD STIX bundle.",
        default=HttpUrl(
            "https://spaceshield.esa.int/stix/space-attack.json"
        ),
    )
    #This field is for the confidence level (by default for the external imports is 75)
    confidence_level: int = Field(
        description="Confidence level for imported objects (0-100).",
        default=75,
    )
    #This field is for the author of the KB
    author_name: str = Field(
        description="Name of the identity that will own imported objects.",
        default="European Space Agency (ESA)",
    )
    #This field is for the type of the author
    author_identity_class: str = Field(
        description="STIX identity class for the author.",
        default="organization",
    )

class ConnectorSettings(BaseConnectorSettings):
    connector: ExternalImportConnectorConfig = Field(
        default_factory=ExternalImportConnectorConfig
    )
    spaceshield: SpaceShieldConfig = Field(
        default_factory=SpaceShieldConfig
    )