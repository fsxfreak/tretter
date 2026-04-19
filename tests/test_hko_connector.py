import json
from connectors.types import ObservationType
import datetime as dt
import responses
from connectors.HkoConnector import HkoConnector
import logging
import pytest
import niquests

logger = logging.getLogger(__name__)
SAMPLE_DATA = "sample_responses/data-weather-gov-hk-weatherapi-opendata-weatherphp.json"


@responses.activate
def test_observe_retrieves_temperature():
    with open(SAMPLE_DATA, "r") as f:
        mock_json = json.load(f)
        responses.get(
            HkoConnector.API_URL,
            json=mock_json,
            status=200,
        )

    connector = HkoConnector()
    observations = connector.observe()

    found_observation = False
    for observation in observations:
        assert observation.sample.timestamp == dt.datetime.fromisoformat(
            "2026-04-20T06:00:00+08:00"
        ).astimezone(tz=dt.timezone.utc)

        if observation.metadata.friendly_name == "Hong Kong Observatory":
            assert observation.sample.value == 25
            assert observation.type == ObservationType.TEMPERATURE
            found_observation = True

    assert found_observation, "No expected observation found"


@responses.activate
def test_observe_server_error():
    responses.get(
        HkoConnector.API_URL,
        status=500,
    )

    connector = HkoConnector()
    with pytest.raises(Exception):
        connector.observe()


@responses.activate
def test_observe_network_error():
    responses.get(
        HkoConnector.API_URL,
        body=niquests.exceptions.ConnectionError("Mocked Connection Error"),
    )

    connector = HkoConnector()
    with pytest.raises(niquests.exceptions.ConnectionError):
        connector.observe()
