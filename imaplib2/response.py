import re


list_re = re.compile(r'\((.*)\) \"(.*)\" \"(.*)\"')


class Response(object):
    # There are three possible server completion responses
    OK = "OK"  # indicates success
    NO = "NO"  # indicates failure
    BAD = "BAD"  # indicates a protocol error


class ListResponse(object):
    def __init__(self, list_response):
        match = list_re.match(list_response)
        self.attributes = match.group(1).split()
        self.hierarchy_delimiter = match.group(2)
        self.name = match.group(3)
