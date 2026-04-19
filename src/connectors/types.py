from enum import auto, Enum
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple


@dataclass
class Sample:
    timestamp: datetime
    value: float


@dataclass
class Metadata:
    friendly_name: str
    coordinates: Tuple[float, float]


class ObservationType(Enum):
    TEMPERATURE = auto()


@dataclass
class Observation:
    type: ObservationType
    sample: Sample
    metadata: Metadata

    def __str__(self):
        return (
            f"Observation(type={self.type.name}, sample=Sample({self.sample.timestamp.isoformat()},"
            f" {self.sample.value}), metadata={self.metadata})"
        )


class Connector(ABC):
    @property
    def headers(self):
        # TODO maybe use pydantic here if more configurability needed
        return {"User-Agent": f"(tretter, {os.getenv('USER_AGENT_EMAIL', 'tretter')})"}

    @abstractmethod
    def observe(self) -> List[Observation]:
        pass
