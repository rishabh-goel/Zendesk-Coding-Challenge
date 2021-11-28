
import sys
from os.path import dirname, abspath
from requesthandler import APIHandler
from clidisplay import View

sys.path.insert(0, dirname(dirname(abspath(__file__))))


class Main:
    def __init__(self):
        self.view = View()  # Object of View class instantiated
        self.api = APIHandler()  # Object of APIHandler class instantiated
        self.input = ""  # User Input
        self.currID = 999  # Default Ticket ID
        self.curr_page = 999  # Default Page number

    def run(self):  # Driver method
        self.display_menu()

    def get_input(self):  # Prompts user for input
        self.input = input()

    def display_menu(self):  # Displays Main menu
        self.view.start_message()
        while True:
            self.get_input()  # Get user input
            if self.input == "menu":  # Display app menu
                self.view.display_menu()

            elif self.input == '1':  # Show all tickets
                response = self.show_all_tickets()
                if response is None:
                    print("\n!!!!!NO TICKETS FOUND!!!!!\n")
                    self.view.display_message("\nEnter '1' to get all tickets, '2' to get a particular ticket, 'quit' to quit the program and 'menu' to go back to the Main Menu: ", 0)

            elif self.input == '2':  # Show one ticket
                response = self.show_one_ticket()
                if response is False:
                    print("\n!!!!!NO TICKET FOUND!!!!!\n")
                    self.view.display_message("\nEnter '1' to get all tickets, '2' to get a particular ticket, 'quit' to quit the program and 'menu' to go back to the Main Menu: ", 0)

            elif self.input == 'quit':  # Quit app
                sys.exit(self.view.quit())

            else:   # Invalid user input
                self.view.display_message("Invalid input, please enter a valid choice: ", 1)

            self.input = ""

    def show_all_tickets(self):  # Display all tickets divided into pages
        try:
            self.view.fetch_tickets("all")
            tickets = self.api.get_all_tickets()  # Get all tickets
            assert tickets not in [-1, 0, 1, False]
            page = self.view.display_all_tickets(tickets, 1)

        except AssertionError as e:
            self.view.error_code = self.api.error_code
            if tickets == -1:  # No tickets found
                self.view.display_bad_request("No tickets founds")
            elif tickets == 1:  # Can't authenticate with API
                self.view.display_bad_request("API authentication failed or invalid user credentials")
            elif tickets == 0:  # API unavailable
                self.view.display_bad_request("API unavailable. Try again later")
            elif tickets is False:  # Other Failure
                self.view.display_bad_request("Unknown Bad Request")

            self.view.error_code = None
            self.api.error_code = None

            return None

        while True:
            self.get_input()
            if self.input == "menu":  # Show menu
                self.view.display_menu()
                break
            elif self.input == "next":  # Next page
                page += 1
                page = self.view.display_all_tickets(tickets, page)
            elif self.input == "prev":  # Previous page
                page -= 1
                page = self.view.display_all_tickets(tickets, page)
            elif self.input == 'quit':  # Quit app
                sys.exit(self.view.quit())
            else:
                self.view.display_message("Not a valid choice. Choose from 'next', 'prev', 'quit' or 'menu'", 1)

            self.input = ""
            self.curr_page = page

        return 0

    def show_one_ticket(self):  # Display one ticket
        self.view.display_message("Enter the ticket ID: ", 0)  # Enter ticket number
        self.get_input()  # Get ticket ID
        ticket_id = self.input
        self.input = ""

        try:
            self.view.fetch_tickets(ticket_id)  # Get ticket
            ticket = self.api.get_one_ticket(ticket_id)
            assert ticket not in [-1, 0, 1, False]
            self.view.display_one_ticket(ticket)  # Display ticket
            self.currID = int(ticket_id)  # Current ticket ID
            return 0

        except AssertionError as e:
            self.view.error_code = self.api.error_code
            if ticket == 1:  # Can't authenticate with API
                self.view.display_bad_request("API authentication failed or invalid user credentials")
            elif ticket == -1:  # Ticket ID not valid
                self.view.display_bad_request("Not a valid ticket ID")
            elif ticket == 0:  # API unavailable
                self.view.display_bad_request("API unavailable. Please try again later")
            elif ticket is False:  # Other Bad Requests
                self.view.display_bad_request("Unknown Bad Request")

            self.view.error_code = None
            self.api.error_code = None

            return False


if __name__ == '__main__':
    t = Main()
    t.run()  # Starting point of the program
