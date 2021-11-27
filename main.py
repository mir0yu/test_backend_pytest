import requests
import json

from secrets import SECRET_KEY, NAME, BASE_URL, AUTH_URL_FSPO, GROUPS_URL


class User:  # User data may be implement with ArgParse/environment variable...
    """Class for data and auth method"""

    def __init__(self):
        self.name = NAME
        self._login = self.name.replace(" ", "").lower()  # transmitted fullname to login in lowercase without space
        self._password = SECRET_KEY
        self.response = self.auth()
        self.response_json = json.loads(self.response.text)
        self.session_id = self.response_json["result"]["sessionId"]  # assigning session_id from authentication
        # print(f"session id : {self.session_id}; login : {self._login}; password : {self._password}")
        # print(self.response.json())
        # print(self.response.text)
        try:
            self.response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print('ERROR: %s' % e)
        assert self.response_json["error"] is None

    def auth(self):
        """Authentication"""
        data_param = {'serviceLogin': f'{self._login}', 'servicePassword': f'{self._password}'}
        return requests.post(
            f"{BASE_URL}{AUTH_URL_FSPO}",
            data=json.dumps(data_param),
            headers={'Content-type': 'application/json'}
        )


class TestUser:
    user_for_api = User()
    # headers = {
    #     'X-Session-Id': f'{user_for_api.session_id}',
    #     'Content-type': 'application/json'
    # }

    def test_groups(self):
        response = requests.get(BASE_URL + GROUPS_URL)
        response_json = json.loads(response.text)
        # print(response.text)
        # print(self.user.response.text)
        # print(BASE_URL+GROUPS_URL)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print('ERROR: %s' % e)
        assert response_json["error"] is None
        assert response_json["result"] is not None
        for r in response_json["result"]["items"]:
            assert isinstance(r["_id"], str), "groups id must be string"
            assert isinstance(r["name"], str), "groups name must be string"
        return response.text


if __name__ == '__main__':
    print(TestUser().test_groups())
