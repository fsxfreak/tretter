import json
import datetime as dt
from connectors.HkoConnector import HkoConnector
from connectors.types import ValueType
import logging

logger = logging.getLogger(__name__)
SAMPLE_DATA = "sample_responses/data-weather-gov-hk-weatherapi-opendata-weatherphp.json"


async def test_observe_retrieves_temperature(niquests_mock):
    with open(SAMPLE_DATA, "r") as f:
        mock_json = json.load(f)
    route = niquests_mock.get(HkoConnector.API_URL, params=HkoConnector.DEFAULT_PARAMS)
    route.respond(json=mock_json, status_code=200)

    connector = HkoConnector()
    observations = await connector.observe()

    found_observation = False
    for observation in observations:
        assert observation.sample.timestamp == dt.datetime.fromisoformat(
            "2026-04-20T06:00:00+08:00"
        ).astimezone(tz=dt.timezone.utc)

        if observation.metadata.entity_name.name == "hko_kp":
            assert observation.sample.value == 25
            assert observation.metadata.value_type == ValueType.TEMPERATURE
            found_observation = True

    assert found_observation, "No expected observation found"


# TODO test error handling
