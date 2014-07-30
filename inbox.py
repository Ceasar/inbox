"""
Convenience wrapper over imaplib.

http://hg.python.org/cpython/file/2.7/Lib/imaplib.py
"""
import email
import imaplib


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


class Server(object):
    """
    Represents a server that supports IMAP connections.
    """
    def __init__(self, host_name, username, password):
        self.host_name = host_name
        self.username = username
        self.password = password

    def connection(self):
        connection = imaplib.IMAP4_SSL(self.host_name)
        connection.login(self.username, self.password)
        return connection

    @property
    def mailboxes(self):
        _, data = self.connection().list()
        return [x for x in data]

    def get_mailbox(self, inbox_name):
        return Mailbox(self.connection(), inbox_name)


class Mailbox(object):
    def __init__(self, connection, name):
        self.connection = connection
        self.name = name
        # Not performing select gets: "SEARCH illegal in state AUTH, only
        # allowed in states SELECTED"
        status, message = self.connection.select(name)
        if status != "OK":
            raise ValueError(message)

    def get_message_ids(self):
        charset, criteria = None, ["ALL"]
        _, data = self.connection.search(charset, *criteria)
        return data[0].split()

    def __getitem__(self, index):
        ids = self.get_message_ids()
        # fetch the email body (RFC822) for the given ID
        message_set, message_parts = ids[index], "(RFC822)"
        _, data = self.connection.fetch(message_set, message_parts)
        # data is a list of tuples of message part envelope and data.
        return Message(data[0][1])


def make_inbox(username, password):
    return Server('imap.gmail.com', username, password)
