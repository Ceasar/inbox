"""
Convenience wrapper over imaplib.

http://hg.python.org/cpython/file/2.7/Lib/imaplib.py
"""
import email
import imaplib


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


class Connection(object):
    """A connection to an IMAP server."""
    def __init__(self, connection):
        self.connection = connection

    def get_mailbox(self, name):
        """Select a mailbox."""
        # Not performing select gets: "SEARCH illegal in state AUTH, only
        # allowed in states SELECTED"
        status, message = self.connection.select(str(name))
        if status != "OK":
            raise ValueError(message)
        return Mailbox(self, name)

    def list_mailboxes(self):
        """List all the mailboxes."""
        _, data = self.connection.list()
        return data


class Server(object):
    """
    Represents a server that supports IMAP connections.
    """
    def __init__(self, host_name, username, password):
        self.host_name = host_name
        self.username = username
        self.password = password

    def connect(self):
        """Get a connection to an IMAP server."""
        conn = imaplib.IMAP4_SSL(self.host_name)
        try:
            conn.login(self.username, self.password)
        except imaplib.IMAP4_SSL.error as e:
            raise AuthenticationError(e)
        return Connection(conn)


class Mailbox(object):
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
