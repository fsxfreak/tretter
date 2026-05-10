import datetime as dt
import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple

import niquests

from connectors.helpers.request import safe_request
from connectors.types import Connector, Metadata, Observation, ObservationType, Sample

logger = logging.getLogger(__name__)


@dataclass
class _TemperatureData:
    place: str
    value: float
    unit: str


class HkoConnector(Connector):
    API_URL = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php"
    DEFAULT_PARAMS = {
        "dataType": "rhrread",
        "lang": "en",
    }

    def _request_raw_data(self) -> Dict:
        result = safe_request(
            niquests.get, self.API_URL, params=self.DEFAULT_PARAMS, headers=self.headers
        )
        if not result:
            return {}

        return result.json()

    def _parse_data(self, raw_data: Dict) -> Tuple[dt.datetime, List[_TemperatureData]]:
        output = []
        for d in raw_data["temperature"]["data"]:
            output.append(
                _TemperatureData(
                    place=d["place"],
                    value=float(d["value"]),
                    unit=d["unit"],
                )
            )

        timestamp = dt.datetime.fromisoformat(
            raw_data["temperature"]["recordTime"]
        ).astimezone(dt.timezone.utc)
        return timestamp, output

    def observe(self) -> List[Observation]:
        raw_data = self._request_raw_data()
        timestamp, data = self._parse_data(raw_data)

        output = []
        for d in data:
            # TODO retrieve coordinates of location from API (probably cache them)
            obs = Observation(
                ObservationType.TEMPERATURE,
                Sample(timestamp, d.value),
                Metadata(d.place, coordinates=(0, 0)),
            )
            output.append(obs)
        return output

    def __str__(self) -> str:
        return "hko"
