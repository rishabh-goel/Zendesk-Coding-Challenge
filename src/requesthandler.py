import requests
import datetime
import json


class APIHandler:

    def __init__(self, cred_file_path='/Users/rishabhgoel/PycharmProjects/ZendeskChallenge/src/credentials.txt'):
        self.URL = ""
        self.data = {}  # Store ticket data
        with open(cred_file_path) as f:
            variables = json.load(f)

        self.subdomain = variables['subdomain']  # Zendesk API subdomain
        self.login_id = variables['loginID']  # Zendesk API username
        self.password = variables['password']   # Zendesk API password
        self.error_code = None

    # Method to get all tickets or return an appropriate error value
    def get_all_tickets(self):
        tickets_response = self.request_api(True, "")
        if tickets_response in [1, False, None, 0] or "tickets" not in tickets_response:
            if tickets_response is None:     # API authentication failed or invalid user credentials
                return 1
            elif tickets_response == 1:  # API unavailable
                return 0
            elif tickets_response == 0:  # All other bad requests
                return False
            elif tickets_response is False or "tickets" not in tickets_response:  # No tickets exist
                return -1

        elif tickets_response not in [1, False, None, 0] and "tickets" in tickets_response:
            for i in range(len(tickets_response["tickets"])):
                updated, created = self.format_dates(tickets_response["tickets"][i]["updated_at"], tickets_response["tickets"][i]["created_at"])
                tickets_response["tickets"][i]["updated_at"] = str(updated)  # Setting the formatted dates
                tickets_response["tickets"][i]["created_at"] = str(created)  # Setting the formatted dates
            return tickets_response

    # Method to get one ticket details from API and return it, or return appropriate error value
    def get_one_ticket(self, ticket_id):
        tickets_response = self.request_api(False, ticket_id)
        if tickets_response not in [1, False, None, 0] and "ticket" in tickets_response:
            updated, created = self.format_dates(tickets_response["ticket"]["updated_at"], tickets_response["ticket"]["created_at"])
            tickets_response["ticket"]["updated_at"] = str(updated)
            tickets_response["ticket"]["created_at"] = str(created)
            return tickets_response

        elif tickets_response in [1, False, None, 0]:
            if tickets_response is False:
                return -1  # Invalid ticket ID
            elif tickets_response == 1:
                return 0  # If API is unavailable
            elif tickets_response is None:
                return 1  # Invalid user credentials
            elif tickets_response == 0:
                return False  # All other bad requests
            return False

    # Method to connect and query the Zendesk API to fetch tickets
    def request_api(self, all_tickets=True, id=""):

        if all_tickets:
            self.URL = "https://" + self.subdomain + ".zendesk.com/api/v2/tickets.json"
        else:
            self.URL = "https://" + self.subdomain + ".zendesk.com/api/v2/tickets/" + str(id) + ".json"
        try:
            response = requests.get(self.URL, auth=(self.login_id, self.password))
            if response.status_code != 200:
                self.error_code = response.status_code

                if response.status_code == 401:  # Authentication failed
                    return None
                elif response.status_code == 404:  # Invalid ticket ID
                    return False
                elif response.status_code == 503:  # API unavailable
                    return 1
                return 0  # For all other bad requests

            self.data = response.json()
            data = self.data
            next_page = []

            while all_tickets and data["next_page"] is not None and data["next_page"] not in next_page:
                self.URL = data["next_page"]
                next_page.append(self.URL)
                response = requests.get(self.URL, auth=(self.login_id, self.password))
                data = response.json()
                self.data["tickets"].extend(data["tickets"])  # Adding new tickets found in the next API web page.

            return self.data

        except Exception as e:
            return 0

    # Method to convert string to date format
    def format_dates(self, updated_at, created_at):
        t1 = datetime.datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%SZ")
        t2 = datetime.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
        updated_date = "%d-%d-%d %d:%d:%d" % (t1.year, t1.month, t1.day, t1.hour, t1.minute, t1.second)
        created_date = "%d-%d-%d %d:%d:%d" % (t2.year, t2.month, t2.day, t2.hour, t2.minute, t2.second)
        return updated_date, created_date