from flexmock import flexmock
from mock import patch, PropertyMock
from sportsipy.nfl.player import AbstractPlayer
from sportsipy.nfl.roster import Player


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.url = url
            self.reason = 'Bad URL'  # Used when throwing HTTPErrors
            self.headers = {}  # Used when throwing HTTPErrors
            self.status_code = 404
            self.html_contents = html_contents
            self.text = html_contents

    return MockPQ(None)


class TestNFLPlayer:
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
        mock_id = PropertyMock(return_value='BAD')
        player = Player(None)
        type(player)._player_id = mock_id

        result = player._retrieve_html_page()

        assert result is None

    @patch('requests.get', side_effect=mock_pyquery)
    def test_missing_weight_returns_none(self, *args, **kwargs):
        mock_weight = PropertyMock(return_value=None)
        player = Player(None)
        type(player)._weight = mock_weight

        assert not player.weight

    @patch('requests.get', side_effect=mock_pyquery)
    def test_requesting_detailed_season_returns_proper_index(self,
                                                             *args,
                                                             **kwargs):
        mock_detailed_seasons = PropertyMock(return_value=['2017',
                                                           '2018',
                                                           'Career'])
        mock_seasons = PropertyMock(return_value=['2015',
                                                  '2016',
                                                  '2017',
                                                  '2018',
                                                  'Career'])
        player = Player(None)
        type(player)._detailed_stats_seasons = mock_detailed_seasons
        type(player)._season = mock_seasons
        player = player('2018')

        assert player._detailed_stats_index == 1
