import logging
from connectors.types import Connector, Observation
import requests


class HkoConnector(Connector):
    API_URL = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php"
    DEFAULT_PARAMS = {
        "dataType": "rhrread",
        "lang": "en",
    }
    logger = logging.getLogger(__name__)

    def observe(self) -> Observation:
        self.logger.debug("Request: ", self.API_URL, self.DEFAULT_PARAMS, self.headers)

        result = requests.get(
            self.API_URL, params=self.DEFAULT_PARAMS, headers=self.headers
        )
        print(result.headers)
        return None
        # return Observation(Sample(None, 12), Metadata("test"))
