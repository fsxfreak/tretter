import logging
from connectors.HkoConnector import HkoConnector
from dotenv import load_dotenv


def main():
    conn = HkoConnector()
    conn.observe()
    pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()
    main()
