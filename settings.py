import os


class Settings:
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    SENTRY_ENVIRONMENT = os.getenv('SENTRY_ENVIRONMENT')

    UNTI_ID = os.getenv('UNTI_ID')
    LRS_SERVER_URL = os.getenv('LRS_SERVER_URL')
    LRS_AUTH = os.getenv('LRS_AUTH')
    LRS_CULTURE_COMPETENCE = os.getenv('LRS_CULTURE_COMPETENCE')

    KAFKA_SERVER = os.getenv('KAFKA_SERVER')

    FS_SERVER_URL = os.getenv('FS_SERVER_URL')
    FS_SERVER_TOKEN = os.getenv('FS_SERVER_TOKEN')

    DP_SERVER_URL = os.getenv('DP_SERVER_URL')
    DP_SERVER_TOKEN = os.getenv('DP_SERVER_TOKEN')
    DP_COMPETENCE_UUID = os.getenv('DP_COMPETENCE_UUID')
    DP_CREATE_ENTRY = os.getenv('DP_CREATE_ENTRY')

    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')

    CARRIER_SERVER_URL = os.getenv('https://carrier.2035.university')
    CARRIER_SERVER_TOKEN = os.getenv('secret_token')

settings = Settings()