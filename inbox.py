import email
import imaplib


class Email(object):
    """
    :param message: an email.message.Message object
    """
    def __init__(self, message):
        self._message = message

    @property
    def headers(self):
        return dict(self._message.items())

    @property
    def body(self):
        for part in self._message.walk():
            print dir(part)
        return [
            {'payload': str(part.get_payload()),
             'Content-Type': part.get_content_type()}
            for part in self._message.walk()
            if not part.is_multipart()]


class Inbox(object):
    def __init__(self, imap4_client):
        self._mail = imap4_client

    def login(self, username, password):
        self._mail.login(username, password)
        self._mail.select("inbox")

    def __getitem__(self, index):
        _, data = self._mail.search(None, "ALL")
        # ids is a space separated string
        ids = data[0].split()
        # fetch the email body (RFC822) for the given ID
        _, data = self._mail.fetch(ids[index], "(RFC822)")
        # NOTE: second value seems irrelevant?, i.e. ')'
        message = email.message_from_string(data[0][1])
        return Email(message)


def make_inbox(username, password):
    host_name = 'imap.gmail.com'
    imap4_client = imaplib.IMAP4_SSL(host_name)
    inbox = Inbox(imap4_client)
    inbox.login(username, password)
    return inbox
