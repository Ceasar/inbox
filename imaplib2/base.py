"""
This module defines the basic components used to interface with an IMAP server.
"""
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
        """Get a raw connection to an IMAP server."""
        return imaplib.IMAP4_SSL(self.host_name)


class Connection(object):
    """A connection to an IMAP server."""
    def __init__(self, server, connection=None):
        self.server = server
        self.__connection = connection or server.raw_connection()

    def close(self):
        """
        Permanently remove all messages that have the \Deleted flag set
        from the currently selected mailbox, and returns to the authenticated
        state from the selected state
        """
        return self.__connection.close()

    # TODO: Determine what this is fetching
    def fetch(self, uid, message_parts=("RFC822",)):
        """Retrieve data associated with a message in the mailbox.

        :param uid:
            The unique identifier for the message.

        :param message_parts:
            Optional. pass. Defaults to ``('RFC822',)``, which retrieves the
            entire message, including the header and is compatible with the
            ``email`` library.
        """
        _, data = self.__connection.uid(
            'fetch',
            uid,
            "(%s)" % " ".join(message_parts)
        )
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
        """Inform the server that the client is done with the connection."""
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
        _, data = self.__connection.uid('search', charset, *criteria)
        return data[0].split()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.logout()
        if type is not None:
            raise type(value)


class Mailbox(object):
    """
    A Mailbox represents a remote folder of messages.
    """
    def __init__(self, connection, name):
        self.__connection = connection
        self.name = name

    def fetch(self, uid):
        data = self.__connection.fetch(uid)
        s = data[0][1]
        message = email.message_from_string(s)
        return Message(uid, message)

    def __iter__(self):
        for message_id in self.__connection.search():
            yield message_id

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.__connection.close()
        if type is not None:
            raise type(value)


class Message(object):
    """
    :param uid:
        A unique identifier string.

    :param message:
        An email.message.Message object.
    """
    def __init__(self, uid, message):
        self.uid = uid
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

    @property
    def raw(self):
        return self._message.as_string()
