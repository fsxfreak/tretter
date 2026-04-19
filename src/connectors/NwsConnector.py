import niquests
import logging
from enum import Enum
from dataclasses import dataclass
import datetime as dt
from connectors.types import Connector, Observation, Metadata, Sample, ObservationType
from typing import List, Dict, Iterator


logger = logging.getLogger(__name__)


class _QualityControl(Enum):
    V = "V"  # verified
    Z = "Z"  # preliminary
    NULL = "null"  # missing


@dataclass
class _PropertyData:
    unit_code: str
    value: float
    quality_control: _QualityControl


class NwsConnector(Connector):
    BASE_API_URL = "https://api.weather.gov"
    OBSERVATIONS_LATEST_PATH = "/observations/latest"
    DEFAULT_STATIONS = ["KJFK"]
    DEFAULT_PARAMS = {"require_qc": "true"}
    PROPERTIES_MAP = {
        "temperature": ObservationType.TEMPERATURE,
    }

    def __init__(self, stations: List[str] = []):
        if not stations:
            stations = self.DEFAULT_STATIONS
        self.stations = stations

    def _make_url(self, station: str) -> str:
        return f"{self.BASE_API_URL}/stations/{station}{self.OBSERVATIONS_LATEST_PATH}"

    def _request_raw_data(self) -> Dict[str, Dict]:
        station_data = {}
        for station in self.stations:
            result = niquests.get(
                self._make_url(station),
                params=self.DEFAULT_PARAMS,
                headers=self.headers,
            )
            station_data[station] = result.json()

        return station_data

    def _parse_metadata(self, station_data: Dict) -> Metadata:
        friendly_name = station_data["properties"]["stationName"]

        geometry = station_data["geometry"]
        coordinates = (0, 0)
        if geometry["type"] == "Point":
            coordinates = (geometry["coordinates"][0], geometry["coordinates"][1])
        else:
            logger.error(
                f"Unsupported geometry type, cannot parse coordinates from {geometry}",
            )

        return Metadata(friendly_name, coordinates)

    def _parse_property_data(self, station_data: Dict) -> Dict[str, _PropertyData]:
        property_data = {}
        for property in self.PROPERTIES_MAP:
            data = station_data["properties"][property]
            property_data[property] = _PropertyData(
                data["unitCode"], data["value"], data["qualityControl"]
            )
        return property_data

    def _parse_station_data(self, station_data: Dict) -> Iterator[Observation]:
        timestamp = dt.datetime.fromisoformat(
            station_data["properties"]["timestamp"]
        ).astimezone(dt.timezone.utc)
        properties = self._parse_property_data(station_data)

        for property_name, property_data in properties.items():
            if property_data.quality_control != _QualityControl.V.value:
                logger.warning(
                    f"Skipping non-verified data {property_name}: {property_data}"
                )
                continue

            observation_type = self.PROPERTIES_MAP[property_name]
            sample = Sample(timestamp, property_data.value)
            metadata = self._parse_metadata(station_data)
            yield Observation(observation_type, sample, metadata)

    def _parse_data(self, station_data: Dict) -> Iterator[Observation]:
        for station in self.stations:
            yield from self._parse_station_data(station_data[station])

    def observe(self) -> List[Observation]:
        raw_data = self._request_raw_data()
        return list(self._parse_data(raw_data))
