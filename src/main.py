import logging
from connectors.HkoConnector import HkoConnector
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def main():
    conn = HkoConnector()
    observations = conn.observe()
    formatted_obs = "\n".join(str(obs) for obs in observations)
    logger.info(f"observations:\n{formatted_obs}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()
    main()
