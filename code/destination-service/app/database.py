import logging

class DatabaseManager:
    @staticmethod
    def log_data(data):
        logging.info(f"Received data: {data}")
