from imaplib2 import ListResponse


def test_parse_list_response():
    raw_list_response = '(\Noselect \HasChildren) "/" "[Gmail]"'
    list_response = ListResponse(raw_list_response)
    assert list_response.attributes == ['\Noselect', '\HasChildren']
    assert list_response.hierarchy_delimiter == "/"
    assert list_response.name == "[Gmail]"
