import unittest
from unittest.mock import patch
import json
import sys
from os.path import dirname, abspath

from src.clidisplay import View
from src.requesthandler import APIHandler
from src.main import Main

sys.path.insert(0, dirname(dirname(abspath(__file__))))


class MockResponse:
    def __init__(self, json_data="", status_code=""):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def test_get_one_ticket(url="", auth=""):
    with open('/Users/rishabhgoel/PycharmProjects/ZendeskChallenge/test/testData.json', 'r') as f:
        j = json.load(f)

    mockObject = MockResponse(j, 200)
    return mockObject


def test_get_all_tickets(url="", auth=""):  # Sample json ticket data for bulk tickets
    with open('/Users/rishabhgoel/PycharmProjects/ZendeskChallenge/test/testDataComplete.json', 'r') as f:
        j = json.load(f)

    mockObject = MockResponse(j, 200)
    return mockObject


def test_get_bad_request_response(url="", auth=""):
    mockObject = MockResponse(status_code=400)
    return mockObject


def test_get_unauthorized_response(url="", auth=""):
    mockObject = MockResponse(status_code=401)
    return mockObject


def test_api_unavailable_response(url="", auth=""):
    mockObject = MockResponse(status_code=503)
    return mockObject


def test_invalid_ticket_id_response(url="", auth=""):
    mockObject = MockResponse({'error': 'RecordNotFound', 'description': 'Not found'}, 404)
    return mockObject


# Tests for requesthandler.py
class APITester(unittest.TestCase):
    #  unit test to get one ticket from API
    @patch('requests.get', side_effect=test_get_one_ticket)
    def test_api_get_one(self, test_get):
        api = APIHandler()
        ticket_response = api.request_api(False, 12)
        self.assertEqual(len(ticket_response), 1)
        assert "ticket" in ticket_response
        self.assertEqual(ticket_response["ticket"]["id"], 12)

    # unit test to get all tickets from API
    @patch('src.requesthandler.requests.get', side_effect=test_get_all_tickets)
    def test_api_get_all(self, test_get):
        api = APIHandler()
        ticket_response = api.request_api(True)
        self.assertEqual(len(ticket_response["tickets"]), 100)
        assert "tickets" in ticket_response
        assert "next_page" in ticket_response
        assert "previous_page" in ticket_response
        assert "count" in ticket_response

    # unit test to check for date format
    def test_date_formatting(self):  # test date is formatted correctly
        api = APIHandler()
        updated, created = api.format_dates("2021-11-25T20:35:46Z", "2021-11-25T20:35:46Z")
        self.assertEqual(updated, "2021-11-25 20:35:46")
        self.assertEqual(created, "2021-11-25 20:35:46")

    # unit test to get bad request response from API
    @patch('src.requesthandler.requests.get', side_effect=test_get_bad_request_response)
    def test_bad_request(self, test_get):
        api = APIHandler()
        # Checking that api.getAllTickets() returns False
        self.assertEqual(api.get_all_tickets(), False)
        # Checking that api.getOneTicket() returns False
        self.assertEqual(api.get_one_ticket('1'), False)

    # unit test to get unauthorized response from API
    @patch('src.requesthandler.requests.get', side_effect=test_get_unauthorized_response)
    def test_unauthorized_request(self, test_get):
        api = APIHandler()
        # Checking that api.getAllTickets() returns 1
        self.assertEqual(api.get_all_tickets(), 1)
        # Checking that api.getOneTicket() returns 1
        self.assertEqual(api.get_one_ticket('1'), 1)

    # unit test to get unavailable response from API
    @patch('src.requesthandler.requests.get', side_effect=test_api_unavailable_response)
    def test_api_unavailable_request(self, mock_test):
        api = APIHandler()
        # Checking that api.getAllTickets() returns 0
        self.assertEqual(api.get_all_tickets(), 0)
        # Checking that api.getTicket() returns 0
        self.assertEqual(api.get_one_ticket('1'), 0)

    # unit test to get invalid ticket ID response from API
    @patch('src.requesthandler.requests.get', side_effect=test_invalid_ticket_id_response)
    def test_invalid_ticket_id_request(self, test_get):
        api = APIHandler()
        self.assertEqual(api.get_one_ticket('1234'), -1)


# Tests for clidisplay.py module
class DisplayTester(unittest.TestCase):
    # unit test to check the basic functionality of view is working as expected
    def test_view(self):
        j1 = test_get_one_ticket()
        j2 = test_get_all_tickets()
        view = View()
        self.assertEqual(view.display_one_ticket(j1.json_data), 0)
        self.assertEqual(view.display_all_tickets(j2.json_data, 1), 1)
        self.assertEqual(view.start_message(), 0)
        self.assertEqual(view.quit(), 0)
        self.assertEqual(view.fetch_tickets("all"), 0)
        self.assertEqual(view.display_menu(), 0)


# Tests for main.py module
class ControllerTester(unittest.TestCase):
    # unit test to test quitting of the application
    @patch("builtins.input", return_value='quit')
    def test_user_quit(self, input):
        controller = Main()
        with self.assertRaises(SystemExit) as cm:
            controller.display_menu()
        self.assertEqual(cm.exception.code, 0)

    # unit test to test pagination
    @patch("builtins.input", side_effect=['1', 'next', 'quit'])
    @patch('src.requesthandler.requests.get', side_effect=test_get_all_tickets)
    def test_show_all(self, input, test_get):
        controller = Main()
        with self.assertRaises(SystemExit) as cm:
            controller.display_menu()
        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(controller.curr_page, 2)

    # unit test to test for multiple ticket IDs
    @patch("builtins.input", side_effect=['20', '30', '40'])
    @patch('src.requesthandler.requests.get', side_effect=test_get_one_ticket)
    def test_show_one(self, input, test_get):  # unit test
        controller = Main()
        self.assertEqual(controller.show_one_ticket(), 0)
        self.assertEqual(controller.currID, 20)
        self.assertEqual(controller.show_one_ticket(), 0)
        self.assertEqual(controller.currID, 30)
        self.assertEqual(controller.show_one_ticket(), 0)
        self.assertEqual(controller.currID, 40)

    # unit test to validate invalid ticket ID request response
    @patch("builtins.input", side_effect=['1234'])  # Ticket ID 199 doesn't exist. Testing that we get invalid response.
    @patch('src.requesthandler.requests.get', side_effect=test_invalid_ticket_id_response)
    def test_invalid_ticket_id(self, input, test_get):
        controller = Main()
        self.assertEqual(controller.show_one_ticket(), False)  # Invalid ticket ID gets False response from showTicket()


if __name__ == "__main__":
    unittest.main()
