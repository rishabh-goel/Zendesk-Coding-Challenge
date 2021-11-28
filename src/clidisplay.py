import math


class View:
    def __init__(self):
        self.page_limit = 25
        self.error_code = None

    def start_message(self):  # Displays Start message
        print("\n\n-------------------------WELCOME TO THE ZENDESK TICKET VIEWER-------------------------")
        print("Enter '1' to get all tickets, '2' to get a particular ticket, 'quit' to quit the program and 'menu' to go back to the Main Menu: ", end="")
        return 0

    def display_bad_request(self, message):  # Displays bad request message
        if self.error_code is not None:
            print("\nError getting data from API. Error Code:", self.error_code)
        print(message)
        return 1

    def display_message(self, message, type):
        print(message, end="")
        return type  # Returns 0 for input or 1 for error

    def display_menu(self):  # Displays Command Menu
        print("\nCommand Options:")
        print("Enter 1 to display all tickets")
        print("Enter 2 to display single ticket")
        print("Enter quit to exit application")
        print("Enter 'menu' to display Menu")
        print("\nEnter your choice:", end="")
        return 0

    def quit(self):  # Displays quit message and quits the App.
        print("\nExiting Application.....")
        return 0

    def fetch_tickets(self, ticket_id):  # Displays loading tickets message on CLI screen
        if ticket_id == "all":
            print("\nFetching tickets, please wait.....")
        else:
            print("\nFetching ticket", ticket_id + ",", "please wait.....")
        return 0

    def display_all_tickets(self, ticket_response, page_num):  # Displays all tickets details with pagination
        ticketsArr = ticket_response["tickets"]

        # Finding number of pages
        total_pages = math.ceil(float(len(ticketsArr)) / float(self.page_limit))

        if page_num > total_pages:
            page_num = 1
        elif page_num < 1:
            page_num = total_pages

        pageTickets = 0
        ticketOffset = (page_num - 1) * self.page_limit

        print("|" + "{0:^16}".format("Ticket Status") + "|" + "{0:^18}".format("Ticket Number") + "|" + "{0:^18}".format("Requester ID") + "|" + "{0:^50}".format("Subject") + "|"  + "{0:^23}".format("Updated Date") + "|")
        print("---------------------------------------------------------------------------------------------------------------------------------------")

        for i in range(int(ticketOffset), int(self.page_limit + ticketOffset)):
            if i < len(ticketsArr):
                if ticketsArr[i]["id"] is None:
                    continue
                else:
                    print("|" + "{0:^16}".format(ticketsArr[i]["status"].upper()) + "|",
                          "{0:^15}".format(ticketsArr[i]["id"]), " | ",
                          "{0:^14}".format(ticketsArr[i]["requester_id"]), " | ",
                          "{0:<46}".format(ticketsArr[i]["subject"]), " | ",
                          "{0:^16}".format(ticketsArr[i]["updated_at"]), " | ")

                pageTickets += 1

        print("\nPage", page_num, "of", total_pages)
        print("\nEnter 'next' to go down, 'prev' to go up, 'menu' for menu and 'quit' for quit: ", end="")
        return page_num  # Current page no

    def display_one_ticket(self, ticket_response):  # Displays one ticket details
        print("|" + "{0:^16}".format("Ticket Status") + "|" + "{0:^18}".format("Ticket Number") + "|" + "{0:^18}".format("Requester ID") + "|" + "{0:^50}".format("Subject") + "|"   "{0:^23}".format("Updated Date") + "|")
        print("---------------------------------------------------------------------------------------------------------------------------------------")

        if "ticket" in ticket_response:
            print("|" + "{0:^16}".format(ticket_response["ticket"]["status"].upper()) + "|",
                  "{0:^16}".format(ticket_response["ticket"]["id"]), "|",
                  "{0:^16}".format(ticket_response["ticket"]["requester_id"]), "|",
                  "{0:<48}".format(ticket_response["ticket"]["subject"]), "|",
                  "{0:^21}".format(ticket_response["ticket"]["updated_at"]), "|")

            print("\nEnter '1' to get all tickets, '2' to get a particular ticket, 'quit' to quit the program and 'menu' to go back to the Main Menu: ", end="")
            return 0
        else:
            return 1