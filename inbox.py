import email
import imaplib


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
        most_recent_email = data[0][1]
        m = email.message_from_string(most_recent_email)
        e = dict(m.items())
        e['body'] = [part.get_payload() for part in m.walk()
                     if part.get_content_type() == 'text/plain']
        return e


def make_inbox(username, password):
    host_name = 'imap.gmail.com'
    imap4_client = imaplib.IMAP4_SSL(host_name)
    inbox = Inbox(imap4_client)
    inbox.login(username, password)
    return inbox
