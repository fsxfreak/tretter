from dataclasses import dataclass
import logging
from connectors.types import Connector, Observation, ObservationType, Sample, Metadata
import requests
from typing import List, Dict, Tuple
import datetime as dt

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

    def __init__(self):
        pass

    def _request_raw_data(self) -> Dict:
        result = requests.get(
            self.API_URL, params=self.DEFAULT_PARAMS, headers=self.headers
        )
        return result.json()

    def _parse_data(self, raw_data: Dict) -> Tuple[dt.datetime, List[_TemperatureData]]:
        output = []
        for d in raw_data["temperature"]["data"]:
            output.append(
                _TemperatureData(
                    place=d["place"],
                    value=d["value"],
                    unit=d["unit"],
                )
            )

        timestamp = dt.datetime.fromisoformat(raw_data["temperature"]["recordTime"])
        return timestamp, output

    def observe(self) -> List[Observation]:
        raw_data = self._request_raw_data()
        timestamp, data = self._parse_data(raw_data)

        output = []
        for d in data:
            obs = Observation(
                ObservationType.TEMPERATURE,
                Sample(timestamp, d.value),
                Metadata(d.place),
            )
            output.append(obs)
        return output
