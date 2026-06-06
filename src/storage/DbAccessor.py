import uuid
from connectors.types import Observation, Metadata, Sample, EntityName

import duckdb
import pathlib

CREATE_METADATA_TABLE = """
CREATE TABLE IF NOT EXISTS event_metadata(
    entity_name VARCHAR PRIMARY KEY,
    value_type VARCHAR,
    friendly_name VARCHAR,
    location GEOMETRY 
)
"""

CREATE_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY,
    entity_name VARCHAR REFERENCES event_metadata(entity_name),
    value FLOAT,
    timestamp DATE
)
"""


class DbAccessor:
    # TODO make this generic over connections?
    def __init__(self, db_conn: duckdb.DuckDBPyConnection):
        self.db_conn = db_conn
        self._ensure_tables()

    @classmethod
    async def connect(cls, db_filename: str | None):
        if db_filename:
            db_path = pathlib.Path(db_filename)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            connection = duckdb.connect(db_path)
            return cls(connection)
        else:
            # in memory db
            connection = duckdb.connect()
            return cls(connection)

    def _ensure_tables(self) -> None:
        self.db_conn.execute(CREATE_METADATA_TABLE)
        self.db_conn.execute(CREATE_EVENTS_TABLE)

    async def _ensure_metadata(self, m: Metadata) -> None:
        geom = f"POINT ({m.coordinates.latitude} {m.coordinates.longitude})"
        self.db_conn.execute(
            """INSERT OR IGNORE INTO
            event_metadata (entity_name, value_type, friendly_name, location)
            VALUES (?, ?, ?, ?)
            """,
            (
                m.entity_name.name,
                m.value_type.value,
                m.friendly_name,
                geom,
            ),
        )

    async def _insert_sample(self, entity_name: EntityName, s: Sample) -> None:
        self.db_conn.execute(
            """INSERT INTO events (id, entity_name, value, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (
                uuid.uuid4(),
                entity_name.name,
                s.value,
                s.timestamp,
            ),
        )

    async def persist_observation(self, observations: list[Observation]) -> None:
        for obs in observations:
            await self._ensure_metadata(obs.metadata)
            await self._insert_sample(obs.metadata.entity_name, obs.sample)
