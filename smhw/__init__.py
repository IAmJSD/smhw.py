"""
    Title: smhw.py
    Description: The unofficial Python API for Show My Homework.
    Author: JakeMakesStuff
    License: GNUv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""

import logging, inspect, asyncio, json, requests, threading, dateutil.parser
# Imports go here.

class student_client:

    logged_in = False
    # Boolean to show if logged in or not.

    delay = 15
    # The delay before checking again.

    class profile:
        json_raw, smhw_token, access_token, refresh_token, token_expire, username, subdomain, student_id, avatar, forename, school_id,  surname, year, parent_ids, gender, sims_id, class_group_ids =\
            None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
    # Defining profile for later.

    client_id = "a44486a71714841f51744b66582427f2c094e48675b40530341d470c26d63bbd"
    # The SMHW client ID.

    client_secret = "243a91065893d1e701d7f5d4ddf6d564a0e0559dfe872e6e6dfba849440af81d"
    # The SMHW client secret.

    logger = logging.getLogger("smhw")
    # Creates a logger.

    registered_events = dict()
    # A list of registered events.

    events = ["on_ready", "on_homework_set", "on_homework_removed", "on_token_refresh"]
    # A list of events.

    def __init__(self, username, password, subdomain):
        self.username = username
        self.password = password
        self.subdomain = subdomain
    # The required strings on import.

    def event(self, func):
        if func.__name__ in self.registered_events:
            raise Exception('A event of the same type ("' + func.__name__ + '") has already been registered.')
        elif not inspect.iscoroutinefunction(func):
            raise Exception('The event "' + func.__name__ + '" was not asynchronous.')
        elif func.__name__ not in self.events:
            raise Exception('The event "' + func.__name__ + '" is not part of this client.')
        else:
            self.registered_events[func.__name__] = func
            self.logger.info(func.__name__ + " has been registered as an event.")
    # Registers the event.

    def get_profile_data(self):
        response = json.loads(requests.get("https://api.showmyhomework.co.uk/api/students",
                                headers={"Accept": "application/smhw.v3+json",
                                         "Authorization": "Bearer " + self.profile.smhw_token}).text)
        self.profile.json_raw = response["students"][0]
        self.set_profile_data()
    # Gets profile data then sets it.

    def set_profile_data(self):
        self.profile.student_id = self.profile.json_raw["id"]
        self.profile.avatar = self.profile.json_raw["avatar"]
        self.profile.forename = self.profile.json_raw["forename"]
        self.profile.surname = self.profile.json_raw["surname"]
        self.profile.year = self.profile.json_raw["year"]
        self.profile.parent_ids = self.profile.json_raw["parent_ids"]
        self.profile.gender = self.profile.json_raw["gender"]
        self.profile.sims_id = self.profile.json_raw["sims_id"]
        self.profile.class_group_ids = self.profile.json_raw["class_group_ids"]
    # Sets profile data.

    async def _refresh_token(self):
        while True:
                if self.logged_in:
                    await asyncio.sleep(self.profile.token_expire-30)
                    response = json.loads(requests.post(
                        "https://api.showmyhomework.co.uk/oauth/token?client_id=" + self.client_id + "&client_secret=" + self.client_secret,
                        headers={"Accept": "application/smhw.v3+json"},
                        data={"grant_type": "refresh_token", "refresh_token" : self.profile.refresh_token,
                              "school_id": self.profile.school_id}).text)
                    self.profile.smhw_token = response["smhw_token"]
                    self.profile.access_token = response["access_token"]
                    self.profile.refresh_token = response["refresh_token"]
                    self.profile.token_expire = int(response["expires_in"])
                    self.user_type = response["user_type"]
                    if "on_token_refresh" in self.registered_events:
                        await self.registered_events["on_token_refresh"]()
    # Automagically refreshes the token and runs on_token_refresh if it exists.

    async def _login(self):
        self.logger.info("Logging in using the credentials given.")
        try:
            response = json.loads(requests.get("https://api.showmyhomework.co.uk/api/schools?subdomain=" + self.subdomain + "&limit=1",
                                    headers={"Accept": "application/smhw.v3+json"}).text)
            self.profile.school_id = response["schools"][0]["id"]
        except:
            raise Exception(
                "Could not get the ID of the school. Either your connection is flaky or the subdomain is wrong.")
        try:
            response = json.loads(requests.post(
                "https://api.showmyhomework.co.uk/oauth/token?client_id=" + self.client_id + "&client_secret=" + self.client_secret,
                headers={"Accept": "application/smhw.v3+json"},
                data={"grant_type": "password", "username": self.username, "password": self.password,
                      "school_id": self.profile.school_id}).text)
            self.profile.username, self.profile.subdomain = self.username, self.subdomain
            self.profile.smhw_token = response["smhw_token"]
            self.profile.access_token = response["access_token"]
            self.profile.refresh_token = response["refresh_token"]
            self.profile.token_expire = int(response["expires_in"])
            self.user_type = response["user_type"]
        except:
            raise Exception(
                "Could not seem to be able to login. Either your connection is flaky or the username/password/subdomain is wrong.")
        if self.user_type == "student":
            del self.user_type
        else:
            raise Exception(
                "This API is only intended for students.")
        self.get_profile_data()
        self.logged_in = True
        del self.username, self.password
        if "on_ready" in self.registered_events:
            await self.registered_events["on_ready"]()
    # Logs into the API, gets profile data and runs on_ready if it exists.

    def homework_structure(self, homework_json):
        class homework:
            completed, due_date, description, issued_on, homework_id, homework_url, teacher_name, subject, title, class_group = \
                None, None, None, None, None, None, None, None, None, None
        homework.due_date = dateutil.parser.parse(homework_json["due_on"])
        homework.completed = homework_json["completed"]
        homework.description = homework_json["class_task_description"]
        homework.issued_on = dateutil.parser.parse(homework_json["issued_on"])
        homework.homework_id = homework_json["id"]
        homework.homework_url = "https://www.showmyhomework.co.uk/homeworks/" + str(homework.homework_id)
        homework.teacher_name = homework_json["teacher_name"]
        homework.subject = homework_json["subject"]
        homework.title = homework_json["class_task_title"]
        homework.class_group = homework_json["class_group_name"]
        return homework
    # Structures the homework.

    def get_homeworks(self):
        response = json.loads(requests.get("https://api.showmyhomework.co.uk/api/todos",
                                           headers={"Accept": "application/smhw.v3+json",
                                                    "Authorization": "Bearer " + self.profile.smhw_token}).text)
        homeworks = response["todos"]
        harr = []
        for homework in homeworks:
            homework = self.homework_structure(homework)
            harr.append(homework)
        return harr
    # Gets the homeworks.

    async def _check_for_homework(self):
        while True:
            if self.logged_in:
                response = json.loads(requests.get("https://api.showmyhomework.co.uk/api/todos",
                                        headers={"Accept": "application/smhw.v3+json",
                                        "Authorization": "Bearer " + self.profile.smhw_token}).text)
                homeworks = response["todos"]
                while True:
                    response = json.loads(requests.get("https://api.showmyhomework.co.uk/api/todos",
                                                       headers={"Accept": "application/smhw.v3+json",
                                                                "Authorization": "Bearer " + self.profile.smhw_token}).text)
                    if len(response["todos"])-len(homeworks) >= 1:
                        if "on_homework_set" in self.registered_events:
                            difference = list(set(homeworks)-set(response["todos"]))
                            homeworks = response["todos"]
                            for homework_json in difference:
                                await self.registered_events["on_homework_set"](self.homework_structure(homework_json))
                    elif len(response["todos"])-len(homeworks) <= -1:
                        homeworks = response["todos"]
                        difference = list(set(response["todos"]) - set(homeworks))
                        if "on_homework_removed" in self.registered_events:
                            for homework_json in difference:
                                await self.registered_events["on_homework_removed"](self.homework_structure(homework_json))
                    await asyncio.sleep(self.delay)
    # Checks for new homeworks and triggers on_homework_set if it exists.

    def login(self):
        asyncio.new_event_loop().run_until_complete(self._login())
    # Starts the async loop to login.

    def refresh_token(self):
        asyncio.new_event_loop().run_until_complete(self._refresh_token())
    # Starts the async loop to refresh the token.

    def check_for_homework(self):
        asyncio.new_event_loop().run_until_complete(self._check_for_homework())
    # Starts the async loop to check for homework.

    def run(self):
        threading.Thread(target=self.login).start()
        threading.Thread(target=self.refresh_token).start()
        threading.Thread(target=self.check_for_homework).start()
    # Starts all of the threads.

# A class for all of the student client items.
