import logging

from dotenv import load_dotenv

from connectors.HkoConnector import HkoConnector
from connectors.NwsConnector import NwsConnector

logger = logging.getLogger(__name__)


def main():
    connectors = [
        HkoConnector(),
        NwsConnector(),
    ]

    observations = []
    for connector in connectors:
        logger.info(f"connector: {connector}")
        obs = connector.observe()
        logger.info(f"num observations: {len(obs)}")
        observations.extend(obs)

    logger.info(f"print num observations: {len(observations)}")
    formatted_obs = "\n".join(str(obs) for obs in observations)
    logger.info(f"observations:\n{formatted_obs}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()
    main()
