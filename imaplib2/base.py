import email
import imaplib

import exc
from response import Response, ListResponse


class Server(object):
    """
    Represents a server that supports IMAP connections.
    """
    def __init__(self, host_name):
        self.host_name = host_name

    def connect(self, username, password):
        """Get a connection to an IMAP server."""
        conn = Connection(self)
        conn.login(username, password)
        return conn

    def raw_connection(self):
        """Get a raw connection to the server."""
        return imaplib.IMAP4_SSL(self.host_name)


class Connection(object):
    """A connection to an IMAP server."""
    def __init__(self, server, connection=None):
        self.server = server
        self.__connection = connection or server.raw_connection()

    def fetch(self, message_id):
        # fetch the email body (RFC822) for the given ID
        message_set, message_parts = message_id, "(RFC822)"
        _, data = self.__connection.fetch(message_set, message_parts)
        # data is a list of tuples of message part envelope and data.
        return data

    def list(self, directory="", pattern="*"):
        """Get a list of zero or more untagged ListResponses."""
        _, list_responses = self.__connection.list(directory, pattern)
        return [ListResponse(list_response)
                for list_response in list_responses]

    def login(self, username, password):
        """Establish authentication and enter the authenticated state."""
        try:
            self.__connection.login(username, password)
        except imaplib.IMAP4_SSL.error as e:
            raise exc.AuthenticationError(e)

    def logout(self):
        self.__connection.logout()

    def select(self, mailbox_name):
        """Select a mailbox so that messages in the mailbox can be accessed."""
        # Not performing select gets: "SEARCH illegal in state AUTH, only
        # allowed in states SELECTED"
        status, message = self.__connection.select(str(mailbox_name))
        if status != Response.OK:
            raise ValueError(message)
        return Mailbox(self, mailbox_name)

    def search(self):
        """Get a list of message IDs that fit the search criteria"""
        charset, criteria = None, ["ALL"]
        _, data = self.__connection.search(charset, *criteria)
        return data[0].split()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.logout()


class Mailbox(object):
    """
    A Mailbox represents a remote folder of messages.
    """
    def __init__(self, connection, name):
        self.__connection = connection
        self.name = name

    def fetch(self, message_id):
        data = self.__connection.fetch(message_id)
        s = data[0][1]
        message = email.message_from_string(s)
        return Message(message_id, message)

    def __iter__(self):
        for message_id in self.__connection.search():
            yield message_id


class Message(object):
    """
    :param s: a string
    """
    def __init__(self, id, message):
        # Convert s to an email.message.Message object
        self.id = id
        self._message = message

    @property
    def headers(self):
        return dict(self._message.items())

    @property
    def body(self):
        return [
            {'payload': str(part.get_payload()),
             'Content-Type': part.get_content_type()}
            for part in self._message.walk()
            if not part.is_multipart()]
