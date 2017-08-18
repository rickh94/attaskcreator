"""Tests flask and slack methods."""
import unittest
from attaskcreator.main import findpeople
from slackperson import SlackPerson

USERLIST = {"members": [
    {
        "color": "ffffff",
        "id": "U00000001",
        "name": "jbiden",
        "profile": {
            "email": "jbiden@whitehouse.gov",
            "first_name": "Joe",
            "last_name": "Biden",
            "real_name": "Joe Biden",
            "real_name_normalized": "Joe Biden",
            "team": "T00000001",
            "title": ""
        },
        "real_name": "Joe Biden",
        "team_id": "T00000001",
        "tz": "America/New_York",
        "tz_label": "Eastern Daylight Time",
        "tz_offset": -14400,
    },
    {
        "color": "000000",
        "id": "U00000002",
        "name": "bobama",
        "profile": {
            "email": "bobama@whitehouse.gov",
            "first_name": "Barack",
            "last_name": "Obama",
            "real_name": "Barack Obama",
            "real_name_normalized": "Barack Obama",
            "team": "T00000001"
        },
        "real_name": "Barack Obama",
        "team_id": "T00000001",
        "tz": "America/New_York",
        "tz_label": "Eastern Daylight Time",
        "tz_offset": -14400,
    },
],
}


class TestFindPeople(unittest.TestCase):
    """Test the find people function."""
    def test_find_people(self):
        """Test the findpeople function."""
        people = findpeople(
            'hey @jbiden, @bobama said you were in town', USERLIST)
        for person in people:
            assert isinstance(person, SlackPerson)
            if person.username == 'bobama':
                assert person.userid == 'U00000002'
            elif person.username == 'jbiden':
                assert person.userid == 'U00000001'

        self.assertListEqual(
            findpeople('no one here', USERLIST),
            []
        )
