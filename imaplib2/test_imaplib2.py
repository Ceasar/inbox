from mailbox import Mailbox
from response import ListResponse


def test_parse_list_response():
    raw_list_response = '(\Noselect \HasChildren) "/" "[Gmail]"'
    list_response = ListResponse(raw_list_response)
    assert list_response.attributes == ['\Noselect', '\HasChildren']
    assert list_response.hierarchy_delimiter == "/"
    assert list_response.name == "[Gmail]"


class MockConnection(object):
    def connection(self):
        pass


def test_mailbox():
    connection = MockConnection()
    name = None
    mailbox = Mailbox(connection, name)
    assert mailbox.get_message(1)
