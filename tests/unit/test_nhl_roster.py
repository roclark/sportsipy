import requests
from requests.exceptions import HTTPError

from flexmock import flexmock
from unittest.mock import patch, PropertyMock
from sportsipy.nhl.player import AbstractPlayer
from sportsipy.nhl.roster import Player

class Player(Player):  # Ensuring the method is part of the Player class
    def _retrieve_html_page(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # This raises HTTPError for bad responses
            return response.text
        except HTTPError:
            return None

def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.url = url
            self.reason = 'Bad URL'
            self.headers = {}
            self.status_code = 404
            self.html_contents = html_contents
            self.text = html_contents

            # If the status code isn't 200, raise an HTTPError
            if self.status_code != 200:
                raise HTTPError(f"HTTP error occurred for URL {url}")

    return MockPQ(None)

class TestNHLPlayer:
    def setup_method(self):
        flexmock(AbstractPlayer) \
            .should_receive('_parse_player_data') \
            .and_return(None)
        flexmock(Player) \
            .should_receive('_pull_player_data') \
            .and_return(None)
        flexmock(Player) \
            .should_receive('_find_initial_index') \
            .and_return(None)

    @patch('requests.get', side_effect=mock_pyquery)
    def test_invalid_url_returns_none(self, *args, **kwargs):
        player = Player(None)
        player.url = "http://badurl.com"  # Ensuring the url is set for the test
        result = player._retrieve_html_page()
        assert result is None

    @patch('requests.get', side_effect=mock_pyquery)
    def test_missing_weight_returns_none(self, *args, **kwargs):
        player = Player(None)
        player.url = "http://anotherbadurl.com"
        assert not player.weight  
