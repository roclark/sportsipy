import mock
from flexmock import flexmock
from sportsipy import utils
from sportsipy.nba.nba_utils import _retrieve_all_teams


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents, status_code=200):
            self.status_code = status_code
            self.html_contents = html_contents
            self.text = html_contents
            self.url = url
            self.reason = 'Invalid'
            self.headers = {}

        def __call__(self, div):
            return self.html_contents

    if '2021' in url:
        return MockPQ('<div/>', status_code=404)
    else:
        return MockPQ('<div id="div_totals-team"/>'
                      '<div id="div_totals-opponent"/>')


class TestNBAUtils:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_nba_2020_season_default_to_previous(self, *args, **kwargs):
        flexmock(utils) \
            .should_receive('_find_year_for_season') \
            .and_return(2021)

        _, year = _retrieve_all_teams(None)

        assert year == '2020'
