from connectors.NwsConnector import NwsConnector
import json
from connectors.types import ObservationType
import datetime as dt
import responses
import logging

logger = logging.getLogger(__name__)
SAMPLE_DATA = (
    "sample_responses/api-weather-gov-stations-station-observation-latest.json"
)


@responses.activate
def test_observe_retrieves_temperature():
    connector = NwsConnector()
    url = connector._make_url("KJFK")
    with open(SAMPLE_DATA, "r") as f:
        mock_json = json.load(f)
        responses.get(
            url,
            json=mock_json,
            status=200,
        )

    observations = connector.observe()

    found_observation = False
    for observation in observations:
        assert observation.sample.timestamp == dt.datetime.fromisoformat(
            "2026-04-19T21:51:00+00:00"
        ).astimezone(tz=dt.timezone.utc)

        if (
            observation.metadata.friendly_name
            == "New York, Kennedy International Airport"
        ):
            assert observation.sample.value == 9.4
            assert observation.type == ObservationType.TEMPERATURE
            found_observation = True

    assert found_observation, "No expected observation found"
