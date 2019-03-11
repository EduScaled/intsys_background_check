import json
import aiohttp
from urllib.parse import urljoin

class DPCheck:

    def __init__(self, server_url, token, unti_id, dp_competence_uuid, lrs_culture_value) -> None:
        super().__init__()
        self.server_url = server_url
        self.token = token
        self.unti_id = unti_id
        self.dp_competence_uuid = dp_competence_uuid
        self.lrs_competence_value = lrs_culture_value.get(list(lrs_culture_value.keys())[0])
        

    async def set_user_data(self):
        """
        Вспомогательный метод для записи значения в DP для последюущей проверки
        Необходим в случае неработоспособности элемнетов системы для создания записи
        """

        async with aiohttp.ClientSession() as session:
            url = urljoin(self.server_url, f'/api/v1/user_meta/{self.unti_id}?app_token={self.token}')
            body = [{
                "competence": self.dp_competence_uuid,
                "value": self.lrs_competence_value 
            }]
            async with session.post(url, json=body) as resp:
                if resp.status == 200:
                    json = await resp.json()
                    if json and json.get("status", None) == 0:
                        return True
                    else:
                        return False
                else:
                    return False


    async def get_user_data(self):
        async with aiohttp.ClientSession() as session:
            url = urljoin(self.server_url, f'/api/v1/user/{self.unti_id}?app_token={self.token}')
            async with session.get(url) as resp:
                if resp.status == 200:
                    elements = await resp.json()
                    filtered = [ elem for elem in elements if elem.get('uuid', None) == self.dp_competence_uuid ]
                    if len(filtered) == 1 and filtered[0].get("value", None):
                        dp_response_value = json.loads(filtered[0].get("value", None))
                        if dp_response_value and \
                            str(dp_response_value.get("value", None)) == str(self.lrs_competence_value):
                                return True
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
    
    
    async def check(self, create_entry):
        if create_entry.lower() != "true":
            result = await self.get_user_data()
        else:
            result = await self.set_user_data() and await self.get_user_data()

        return result  
