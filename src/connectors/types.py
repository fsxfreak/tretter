import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


class Connector(ABC):
    @property
    def headers(self):
        return {"User-Agent": f"(tretter, {os.getenv('USER_AGENT_EMAIL', 'tretter')})"}

    @abstractmethod
    def observe(self):
        pass


@dataclass
class Sample:
    timestamp: datetime
    value: float


@dataclass
class Metadata:
    location: str


@dataclass
class Observation:
    sample: Sample
    metadata: Metadata
