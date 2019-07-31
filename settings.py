import os


class Settings:
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    SENTRY_ENVIRONMENT = os.getenv('SENTRY_ENVIRONMENT')

    CULTURE_TEST_UNTI_ID = os.getenv('UNTI_ID')
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

    REMOTE_SELENIUM_HUB_URL = os.getenv('REMOTE_SELENIUM_HUB_URL', "http://selenoid-ui.2035.university/wd/hub")
    UPLOADS_SERVER_URL = os.getenv('UPLOADS_SERVER_URL', "https://uploads.u2035test.ru/")
    UPLOADS_TEST_EVENT_UUID = os.getenv('UPLOADS_TEST_EVENT_UUID', "c96c5f53-beb2-41c2-aeb9-80aa766102da")
    UPLOADS_TEST_FILE_PATH = os.getenv('UPLOADS_TEST_FILE_PATH', os.path.join(os.getcwd(), "checks", "test_data", "test.txt"))
    UPLOADS_TEST_UNTI_ID = os.getenv('UPLOADS_TEST_UNTI_ID', 1002)
    UPLOADS_DELETE_TEST_FILE_TIMEOUT = os.getenv('UPLOADS_DELETE_TEST_FILE_TIMEOUT', 15)

    SSO_LOGIN = os.getenv('SSO_LOGIN', 'minion2+opreeb@yandex.ru')
    SSO_PASSWORD = os.getenv('SSO_PASSWORD', 'minion2^^')

    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')

    CARRIER_SERVER_URL = os.getenv('CARRIER_SERVER_URL', 'http://127.0.0.1:8080')
    CARRIER_SERVER_TOKEN = os.getenv('CARRIER_SERVER_TOKEN', 'secret_token')

settings = Settings()