from connectors.NwsConnector import NwsConnector
from connectors.types import ValueType
import json
import datetime as dt
import logging

logger = logging.getLogger(__name__)
SAMPLE_DATA = (
    "sample_responses/api-weather-gov-stations-station-observation-latest.json"
)


async def test_observe_retrieves_temperature(niquests_mock):
    connector = NwsConnector()
    url = connector._make_url("KJFK")
    with open(SAMPLE_DATA, "r") as f:
        mock_json = json.load(f)
    route = niquests_mock.get(url, params=connector.DEFAULT_PARAMS)
    route.respond(json=mock_json, status_code=200)

    observations = await connector.observe()

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
            assert observation.metadata.value_type == ValueType.TEMPERATURE
            found_observation = True

    assert found_observation, "No expected observation found"
