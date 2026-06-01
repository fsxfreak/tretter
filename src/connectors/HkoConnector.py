import datetime as dt
import logging
from dataclasses import dataclass

import niquests

from connectors.helpers.request import safe_request
from connectors.types import (
    Connector,
    Metadata,
    Observation,
    Sample,
    EntityName,
    ValueType,
    Coordinate,
)

logger = logging.getLogger(__name__)


@dataclass
class _TemperatureData:
    place: str
    value: float
    unit: str


@dataclass(frozen=True)
class _StationCode:
    code: str


_stations: dict[str, _StationCode] = {
    "Beas River": _StationCode("BR1"),
    "Bluff Head": _StationCode("BHD"),
    "Central Pier": _StationCode("CP1"),
    "Cheung Chau": _StationCode("CCH"),
    "Chek Lap Kok": _StationCode("CLK"),
    "Ching Pak House": _StationCode("CPH"),
    "Clear Water Bay": _StationCode("CWB"),
    "Green Island": _StationCode("GI"),
    "Happy Valley": _StationCode("HPV"),
    "Hong Kong Park": _StationCode("HKP"),
    # HKO synoptic station is at the airport
    "Hong Kong Observatory": _StationCode("CLK"),
    "Kai Tak": _StationCode("SE"),
    "Kai Tak Runway Park": _StationCode("SE1"),
    "Kadoorie Farm and Botanic Garden": _StationCode("KFB"),
    "Kat O": _StationCode("KAT"),
    "Kau Sai Chau": _StationCode("KSC"),
    "King's Park": _StationCode("KP"),
    "Kowloon City": _StationCode("KLT"),
    "Kwun Tong": _StationCode("KTG"),
    "Lamma Island": _StationCode("LAM"),
    "Lau Fau Shan": _StationCode("LFS"),
    "Nei Lak Shan": _StationCode("NLS"),
    "New Tsing Yi Station": _StationCode("TY1"),
    "Ngong Ping": _StationCode("NGP"),
    "Pak Tam Chung (Tsak Yue Wu)": _StationCode("TYW"),
    "Peng Chau": _StationCode("PEN"),
    "Ping Chau": _StationCode("EPC"),
    "Sai Kung": _StationCode("SKG"),
    "Sha Lo Wan": _StationCode("SLW"),
    "Sha Tin": _StationCode("SHA"),
    "Sham Shui Po": _StationCode("SSP"),
    "Shau Kei Wan": _StationCode("SKW"),
    "Shek Kong": _StationCode("SEK"),
    "Sheung Shui": _StationCode("SSH"),
    "Stanley": _StationCode("STY"),
    "Ta Kwu Ling": _StationCode("TKL"),
    "Tai Lung": _StationCode("TLS"),
    "Tai Mei Tuk": _StationCode("PLC"),
    "Tai Mo Shan": _StationCode("TMS"),
    "Tai Po": _StationCode("YCT"),
    "Tap Mun": _StationCode("TAP"),
    "Tate's Cairn": _StationCode("TC"),
    "The Peak": _StationCode("VP1"),
    "Tseung Kwan O": _StationCode("JKB"),
    "Tsing Yi": _StationCode("CPH"),
    "Tsuen Wan Ho Koon": _StationCode("TWN"),
    "Tsuen Wan Shing Mun Valley": _StationCode("TW"),
    "Tuen Mun": _StationCode("TU1"),
    "Waglan Island": _StationCode("WGL"),
    "Wetland Park": _StationCode("WLP"),
    "Wong Chuk Hang": _StationCode("HKS"),
    "Wong Tai Sin": _StationCode("WTS"),
    "Yuen Long Park": _StationCode("YLP"),
}

_coordinates = {
    _StationCode("BR1"): Coordinate.from_dms(22, 29, 36, 114, 6, 18),
    _StationCode("BHD"): Coordinate.from_dms(22, 11, 51, 114, 12, 43),
    _StationCode("CP1"): Coordinate.from_dms(22, 17, 20, 114, 9, 21),
    _StationCode("CCH"): Coordinate.from_dms(22, 12, 4, 113, 56, 2),
    _StationCode("CLK"): Coordinate.from_dms(22, 18, 53, 114, 1, 36),
    _StationCode("CPH"): Coordinate.from_dms(22, 20, 53, 114, 6, 33),
    _StationCode("CWB"): Coordinate.from_dms(22, 15, 48, 114, 17, 59),
    _StationCode("GI"): Coordinate.from_dms(22, 17, 6, 114, 6, 46),
    _StationCode("HPV"): Coordinate.from_dms(22, 16, 14, 114, 11, 1),
    _StationCode("HKP"): Coordinate.from_dms(22, 16, 42, 114, 9, 44),
    _StationCode("SE"): Coordinate.from_dms(22, 18, 35, 114, 12, 48),
    _StationCode("SE1"): Coordinate.from_dms(22, 18, 18, 114, 13, 1),
    _StationCode("KFB"): Coordinate.from_dms(22, 25, 58, 114, 7, 15),
    _StationCode("KAT"): Coordinate.from_dms(22, 32, 11, 114, 18, 7),
    _StationCode("KSC"): Coordinate.from_dms(22, 22, 13, 114, 18, 45),
    _StationCode("KP"): Coordinate.from_dms(22, 18, 43, 114, 10, 22),
    _StationCode("KLT"): Coordinate.from_dms(22, 20, 6, 114, 11, 5),
    _StationCode("KTG"): Coordinate.from_dms(22, 19, 7, 114, 13, 29),
    _StationCode("LAM"): Coordinate.from_dms(22, 13, 34, 114, 6, 31),
    _StationCode("LFS"): Coordinate.from_dms(22, 28, 8, 113, 59, 1),
    _StationCode("NLS"): Coordinate.from_dms(22, 15, 48, 113, 54, 40),
    _StationCode("TY1"): Coordinate.from_dms(22, 20, 39, 114, 6, 36),
    _StationCode("NGP"): Coordinate.from_dms(22, 15, 31, 113, 54, 46),
    _StationCode("TYW"): Coordinate.from_dms(22, 24, 10, 114, 19, 23),
    _StationCode("PEN"): Coordinate.from_dms(22, 17, 28, 114, 2, 36),
    _StationCode("EPC"): Coordinate.from_dms(22, 32, 48, 114, 25, 42),
    _StationCode("SKG"): Coordinate.from_dms(22, 22, 32, 114, 16, 28),
    _StationCode("SLW"): Coordinate.from_dms(22, 17, 28, 113, 54, 25),
    _StationCode("SHA"): Coordinate.from_dms(22, 24, 9, 114, 12, 36),
    _StationCode("SSP"): Coordinate.from_dms(22, 20, 9, 114, 8, 13),
    _StationCode("SKW"): Coordinate.from_dms(22, 16, 54, 114, 14, 10),
    _StationCode("SEK"): Coordinate.from_dms(22, 26, 10, 114, 5, 5),
    _StationCode("SSH"): Coordinate.from_dms(22, 30, 7, 114, 6, 40),
    _StationCode("STY"): Coordinate.from_dms(22, 12, 51, 114, 13, 7),
    _StationCode("TKL"): Coordinate.from_dms(22, 31, 43, 114, 9, 24),
    _StationCode("TLS"): Coordinate.from_dms(22, 29, 5, 114, 7, 3),
    _StationCode("PLC"): Coordinate.from_dms(22, 28, 31, 114, 14, 15),
    _StationCode("TMS"): Coordinate.from_dms(22, 24, 38, 114, 7, 28),
    _StationCode("YCT"): Coordinate.from_dms(22, 26, 54, 114, 10, 38),
    _StationCode("TAP"): Coordinate.from_dms(22, 28, 17, 114, 21, 38),
    _StationCode("TC"): Coordinate.from_dms(22, 21, 28, 114, 13, 4),
    _StationCode("VP1"): Coordinate.from_dms(22, 15, 51, 114, 9, 18),
    _StationCode("JKB"): Coordinate.from_dms(22, 18, 57, 114, 15, 20),
    _StationCode("TWN"): Coordinate.from_dms(22, 23, 1, 114, 6, 28),
    _StationCode("TW"): Coordinate.from_dms(22, 22, 32, 114, 7, 36),
    _StationCode("TU1"): Coordinate.from_dms(22, 23, 9, 113, 57, 51),
    _StationCode("WGL"): Coordinate.from_dms(22, 10, 56, 114, 18, 12),
    _StationCode("WLP"): Coordinate.from_dms(22, 28, 0, 114, 0, 32),
    _StationCode("HKS"): Coordinate.from_dms(22, 14, 52, 114, 10, 25),
    _StationCode("WTS"): Coordinate.from_dms(22, 20, 22, 114, 12, 19),
    _StationCode("YLP"): Coordinate.from_dms(22, 26, 27, 114, 1, 6),
}


class HkoConnector(Connector):
    API_URL = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php"
    DEFAULT_PARAMS = {
        "dataType": "rhrread",
        "lang": "en",
    }
    CONNECTOR_NAME = "hko"

    def __init__(self):
        self.metadata_cache: dict[EntityName, Metadata] = {}

    async def _request_raw_data(self) -> dict:
        result = await safe_request(
            niquests.async_api.get,
            self.API_URL,
            params=self.DEFAULT_PARAMS,
            headers=self.headers,
        )
        if not result:
            return {}

        return result.json()

    @classmethod
    def _parse_data(cls, raw_data: dict) -> tuple[dt.datetime, list[_TemperatureData]]:
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

    def _build_entity_name(self, place_name: str) -> EntityName:
        station = _stations[place_name].code.lower()
        return EntityName(f"{self.CONNECTOR_NAME}_{station}")

    def _get_metadata(
        self, data: _TemperatureData, entity_name: EntityName
    ) -> Metadata:
        if entity_name in self.metadata_cache:
            return self.metadata_cache[entity_name]

        station_code = _stations[data.place]
        if data.unit != "C":
            raise Exception("data not expected temperature data")
        metadata = Metadata(
            entity_name,
            ValueType.TEMPERATURE,
            data.place,
            _coordinates[station_code],
        )
        self.metadata_cache[entity_name] = metadata

        return metadata

    async def observe(self) -> list[Observation]:
        raw_data = await self._request_raw_data()
        timestamp, data = self._parse_data(raw_data)

        output = []
        for d in data:
            entity_name = self._build_entity_name(d.place)
            metadata = self._get_metadata(d, entity_name)

            obs = Observation(
                Sample(timestamp, d.value),
                metadata,
            )
            output.append(obs)
        return output

    def __str__(self) -> str:
        return "hko"
