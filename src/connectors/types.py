from enum import auto, Enum
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Sample:
    timestamp: datetime
    value: float


@dataclass
class Metadata:
    location: str


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
        return {"User-Agent": f"(tretter, {os.getenv('USER_AGENT_EMAIL', 'tretter')})"}

    @abstractmethod
    def observe(self) -> List[Observation]:
        pass
