from connectors.NwsConnector import NwsConnector
from connectors.HkoConnector import HkoConnector
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


def main():
    connectors = [
        HkoConnector(),
        NwsConnector(),
    ]

    observations = []
    for connector in connectors:
        observations.extend(connector.observe())

    formatted_obs = "\n".join(str(obs) for obs in observations)
    logger.info(f"observations:\n{formatted_obs}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()
    main()
