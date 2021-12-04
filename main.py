import requests
import json

from secrets import SECRET_KEY, NAME, BASE_URL, AUTH_URL_FSPO, GROUPS_URL, PROFESSORS_URL, SCHEDULE_URL, DEADLINE_URL


class User:  # User data may be implement with ArgParse/environment variable...
    """Class for data and auth method"""

    def __init__(self):
        self.name = NAME
        self._login = self.name.replace(" ", "").lower()  # transmitted fullname to login in lowercase without space
        self._password = SECRET_KEY
        self.response = self.auth()
        self.response_json = json.loads(self.response.text)
        self.session_id = self.response_json["result"]["sessionId"]  # assigning session_id from authentication
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

    def test_groups(self):
        response = requests.get(BASE_URL + GROUPS_URL)
        response_json = json.loads(response.text)
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

    def test_professors(self):
        response = requests.get(BASE_URL + PROFESSORS_URL)
        response_json = json.loads(response.text)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print('ERROR: %s' % e)
        assert response_json["error"] is None
        assert response_json["result"] is not None
        for r in response_json["result"]["items"]:
            assert isinstance(r["_id"], str), "professor id must be string"
            assert isinstance(r["name"], str), "professor name must be string"
        return response.text

    def test_schedule(self):
        _id = self.user_for_api.response_json["result"]["user"]["scheduleUser"]["_id"]
        response = requests.get(BASE_URL + SCHEDULE_URL + _id)
        response_json = json.loads(response.text)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print('ERROR: %s' % e)
        assert response_json["error"] is None
        assert response_json["result"] is not None
        for r in response_json["result"]["items"]:
            assert isinstance(r["_id"], str), "student id must be string"
            assert (r["day"] in ["sun", "mon", "tue", "wed", "thu", "fri", "sat"])
            assert (r["week"] in ["odd", "even"])
            assert isinstance(r["startTime"], str), "Start time must be string"
            assert isinstance(r["endTime"], str), "End time must be string"
            assert isinstance(r["lessonNum"], int), "lesson Number must be int"
            assert (r["type"] in ["lecture", "lab", "practice", "test", "course", None])
            assert isinstance(r["rooms"], str), "rooms must be string"

        return response.text

    def test_create_deadline(self, title="sdjad", description="dasd", date=2378123):
        response = requests.post(
            f"{BASE_URL}{DEADLINE_URL}",
            data=json.dumps(
                {"title": title,
                 "description": description,
                 "date": date}
            ),
            headers={
                'Content-type': 'application/json',
                'X-Session-Id': self.user_for_api.session_id
            }
        )
        response_json = json.loads(response.text)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print('ERROR: %s' % e)
        assert response_json["error"] is None
        assert response_json["result"] is not None
        return response_json["result"]["_id"]

    def test_delete_deadline(self):
        _id = self.test_create_deadline("Это мой 13 дедлайн", "Пока без описания, впредь осторожнее", 1628764738)
        response = requests.delete(
            f"{BASE_URL}{DEADLINE_URL}/{_id}/close",
            headers={
                'Content-type': 'application/json',
                'X-Session-Id': self.user_for_api.session_id
            }
        )
        response_json = json.loads(response.text)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print('ERROR: %s' % e)
        assert response_json["error"] is None
        assert response_json["result"] is not None


if __name__ == '__main__':
    print(TestUser().test_groups())
    print(TestUser().test_professors())
    print(TestUser().test_schedule())
    print(TestUser().test_create_deadline(title="Это мой двенадцатый дедлайн",
                                          description="Пока без описания, впредь осторожнее", date=1628764738))
    print(TestUser().test_delete_deadline())
