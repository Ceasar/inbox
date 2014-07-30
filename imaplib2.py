"""
Convenience wrapper over imaplib.

http://tools.ietf.org/html/rfc3501

http://hg.python.org/cpython/file/2.7/Lib/imaplib.py
"""
import email
import imaplib
import re


class AuthenticationError(Exception):
    pass


class Message(object):
    """
    :param s: a string
    """
    def __init__(self, s):
        # Convert s to an email.message.Message object
        self._message = email.message_from_string(s)

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


list_re = re.compile(r'\((.*)\) \"(.*)\" \"(.*)\"')


class ListResponse(object):
    def __init__(self, list_response):
        match = list_re.match(list_response)
        self.attributes = match.group(1).split()
        self.hierarchy_delimiter = match.group(2)
        self.name = match.group(3)


class Connection(object):
    """A connection to an IMAP server."""
    def __init__(self, host_name, username, password):
        self.connection = imaplib.IMAP4_SSL(host_name)
        self._login(username, password)

    def _login(self, username, password):
        """Establish authentication and enter the authenticated state."""
        try:
            self.connection.login(username, password)
        except imaplib.IMAP4_SSL.error as e:
            raise AuthenticationError(e)

    def select(self, mailbox_name):
        """Select a mailbox so that messages in the mailbox can be accessed."""
        # Not performing select gets: "SEARCH illegal in state AUTH, only
        # allowed in states SELECTED"
        status, message = self.connection.select(str(mailbox_name))
        if status != Response.OK:
            raise ValueError(message)
        return Mailbox(self, mailbox_name)

    def list(self, directory="", pattern="*"):
        """Get a list of zero or more untagged ListResponses."""
        _, list_responses = self.connection.list(directory, pattern)
        return [ListResponse(list_response)
                for list_response in list_responses]


class Response(object):
    # There are three possible server completion responses
    OK = "OK"  # indicates success
    NO = "NO"  # indicates failure
    BAD = "BAD"  # indicates a protocol error


class Server(object):
    """
    Represents a server that supports IMAP connections.
    """
    def __init__(self, host_name, username, password):
        self.host_name = host_name
        self.username = username
        self.password = password

    def connect(self):
        """Get an authenticated connection to an IMAP server."""
        return Connection(self.host_name, self.username, self.password)


class Mailbox(object):
    """
    A Mailbox represents a remote folder of messages.
    """
    def __init__(self, connection, name):
        self.connection = connection
        self.name = name

    def get_message(self, message_id):
        """Fetch an email message."""
        # fetch the email body (RFC822) for the given ID
        message_set, message_parts = message_id, "(RFC822)"
        _, data = self.connection.connection.fetch(message_set, message_parts)
        # data is a list of tuples of message part envelope and data.
        return Message(data[0][1])

    def list_messages(self):
        """Get a list of message IDs that fit the search criteria"""
        charset, criteria = None, ["ALL"]
        _, data = self.connection.connection.search(charset, *criteria)
        return data[0].split()

    def __getitem__(self, index):
        ids = self.list_messages()
        return self.get_message(ids[index])
