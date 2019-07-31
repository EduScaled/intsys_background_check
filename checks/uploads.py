from time import sleep

from urllib.parse import urljoin
from aiologger import Logger
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from checks import _get_kafka_messages
from settings import settings

logger = Logger.with_default_handlers()


class Uploader:
    def __init__(self, remote_selenium_hub, uploads_url, event_uuid, login, password):
        self.remote_selenium_hub = remote_selenium_hub
        self.uploads_url = uploads_url
        self.event_uuid = event_uuid
        self.login = login
        self.password = password

    def _get_proper_upload_div(self, driver):
        material_result_divs = driver.find_elements_by_class_name('material-result-div')
        for div in material_result_divs:
            if '2.1.' in div.text:
                return div

    def upload_file(self, file_path):
        driver = webdriver.Remote(
           command_executor=self.remote_selenium_hub,
           desired_capabilities=DesiredCapabilities.CHROME)
        driver.get(urljoin(self.uploads_url, self.event_uuid))
        try:
            login_field = driver.find_element_by_id("loginEmail")
            login_field.send_keys(self.login)

            password_field = driver.find_element_by_id("loginPassword")
            password_field.send_keys(self.password)

            submit_button = driver.find_element_by_id("sbmt")
            submit_button.click()

            sleep(1)

            upload_my_trace_button = driver.find_element_by_xpath('//a[text()="Загрузить свой след"]')
            upload_my_trace_button.click()

            proper_upload_div = self._get_proper_upload_div(driver)
            proper_upload_div.find_element_by_tag_name('button').click()

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            checkboxes = proper_upload_div.find_elements_by_class_name("result-circle-items")
            for chb in checkboxes:
                chb.click()

            file_field = proper_upload_div.find_element_by_name('file_field')
            file_field.send_keys(file_path)
            sleep(1)
            select_files_btn = proper_upload_div.find_element_by_class_name('select-files-btn')
            select_files_btn.click()

            save_button = proper_upload_div.find_element_by_name('add_btn')
            save_button.click()

            sleep(1)
            result_files_div = proper_upload_div.find_element_by_class_name("result-items-wrapper")
            file_ul = result_files_div.find_element_by_class_name('result-materials-wrapper')
            id = file_ul.get_attribute('data-result-id')
            print(f"Got uploads id: {id}")

            sleep(settings.UPLOADS_DELETE_TEST_FILE_TIMEOUT)

            delete_file_button = file_ul.find_element_by_name("material_id")
            delete_file_button.click()

            alert = driver.switch_to.alert
            alert.accept()
            print(f"Deleted material: {id}")
            return id
        except (WebDriverException, ConnectionError):
            import traceback
            traceback.print_exc()
        finally:
            driver.quit()

        return None


class UploadsResponseCheck:
    async def check(self, uploads_result):
        if uploads_result:
            return True
        return False


class UploadsKafkaCheck:
    @classmethod
    def _get_uploads_ids_from_messages(cls, messages):
        for message in messages:
            try:
                yield message.value['id']['id']
            except KeyError:
                pass

    async def check(self, start, uploads_response):
        messages = await _get_kafka_messages('uploads', start=start)
        return uploads_response in set(self._get_uploads_ids_from_messages(messages))
