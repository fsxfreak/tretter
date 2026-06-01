import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto


@dataclass(frozen=True)
class EntityName:
    name: str


@dataclass
class Sample:
    timestamp: datetime
    value: float


class ValueType(Enum):
    TEMPERATURE = auto()


@dataclass
class Coordinate:
    latitude: float
    longitude: float

    @staticmethod
    def _to_decimal(d: float, m: float, s: float) -> float:
        return d + m / 60 + s / 3600

    @classmethod
    def from_dms(cls, d_lat, m_lat, s_lat, d_lon, m_lon, s_lon) -> "Coordinate":
        return cls(
            cls._to_decimal(d_lat, m_lat, s_lat), cls._to_decimal(d_lon, m_lon, s_lon)
        )

    def __str__(self):
        return f"(lat={self.latitude:.2f}, lon={self.longitude:.2f})"

    def __repr__(self):
        return self.__str__()


@dataclass
class Metadata:
    entity_name: EntityName
    value_type: ValueType

    friendly_name: str
    coordinates: Coordinate


@dataclass
class Observation:
    sample: Sample
    metadata: Metadata

    def __str__(self):
        return (
            f"Observation(Sample({self.sample.timestamp.isoformat()},"
            f" {self.sample.value}), {self.metadata})"
        )


class Connector(ABC):
    @property
    def headers(self):
        # TODO maybe use pydantic here if more configurability needed
        return {"User-Agent": f"(tretter, {os.getenv('USER_AGENT_EMAIL', 'tretter')})"}

    @abstractmethod
    async def observe(self) -> list[Observation]:
        pass
