import mock
import pytest
from flexmock import flexmock
from os.path import join, dirname
from sportsreference import utils
from sportsreference.ncaab.conferences import Conference, Conferences


YEAR = 2018


def read_file(filename):
    filepath = join(dirname(__file__), 'ncaab', filename)
    return open(filepath, 'r', encoding='utf8').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents, status_code=200):
            self.url = url
            self.reason = 'Bad URL'  # Used when throwing HTTPErrors
            self.headers = {}  # Used when throwing HTTPErrors
            self.status_code = status_code
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            return read_file()

    if 'BAD' in url:
        return MockPQ('', 404)
    if 'big-12' in url:
        html_contents = read_file('%s-big-12.html' % YEAR)
        return MockPQ(html_contents)
    if 'big-east' in url:
        html_contents = read_file('%s-big-east.html' % YEAR)
        return MockPQ(html_contents)
    html_contents = read_file('%s.html' % YEAR)
    return MockPQ(html_contents)


def mock_request(url):
    class MockRequest:
        def __init__(self, html_contents, status_code=200):
            self.status_code = status_code
            self.html_contents = html_contents
            self.text = html_contents

    if str(YEAR) in url:
        return MockRequest('good')
    else:
        return MockRequest('bad', status_code=404)


class TestNCAABConferences:
    def setup_method(self):
        team_conference = {'kansas': 'big-12',
                           'texas-tech': 'big-12',
                           'west-virginia': 'big-12',
                           'kansas-state': 'big-12',
                           'texas-christian': 'big-12',
                           'oklahoma-state': 'big-12',
                           'oklahoma': 'big-12',
                           'baylor': 'big-12',
                           'texas': 'big-12',
                           'iowa-state': 'big-12',
                           'xavier': 'big-east',
                           'villanova': 'big-east',
                           'seton-hall': 'big-east',
                           'creighton': 'big-east',
                           'providence': 'big-east',
                           'butler': 'big-east',
                           'marquette': 'big-east',
                           'georgetown': 'big-east',
                           'st-johns-ny': 'big-east',
                           'depaul': 'big-east'}
        conferences_result = {'big-12': {
                                  'name': 'Big 12 Conference',
                                  'teams': {'kansas': 'Kansas',
                                            'texas-tech': 'Texas Tech',
                                            'west-virginia': 'West Virginia',
                                            'kansas-state': 'Kansas State',
                                            'texas-christian':
                                            'Texas Christian',
                                            'oklahoma-state': 'Oklahoma State',
                                            'oklahoma': 'Oklahoma',
                                            'baylor': 'Baylor',
                                            'texas': 'Texas',
                                            'iowa-state': 'Iowa State'}
                                    },
                              'big-east': {
                                    'name': 'Big East Conference',
                                    'teams': {'xavier': 'Xavier',
                                              'villanova': 'Villanova',
                                              'seton-hall': 'Seton Hall',
                                              'creighton': 'Creighton',
                                              'providence': 'Providence',
                                              'butler': 'Butler',
                                              'marquette': 'Marquette',
                                              'georgetown': 'Georgetown',
                                              'st-johns-ny': "St. John's (NY)",
                                              'depaul': 'DePaul'}
                                    }
                              }
        self.team_conference = team_conference
        self.conferences_result = conferences_result

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_conferences_integration(self, *args, **kwargs):
        flexmock(utils) \
            .should_receive('_find_year_for_season') \
            .and_return(YEAR)

        conferences = Conferences()

        assert conferences.team_conference == self.team_conference
        assert conferences.conferences == self.conferences_result

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_conferences_integration_bad_url(self, *args, **kwargs):
        with pytest.raises(ValueError):
            conferences = Conferences('BAD')

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_conference_integration_bad_url(self, *args, **kwargs):
        with pytest.raises(ValueError):
            conference = Conference('BAD')

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_conference_with_no_names_is_empty(self, *args, **kwargs):
        flexmock(Conference) \
            .should_receive('_get_team_abbreviation') \
            .and_return('')

        conference = Conference('big-12')

        assert len(conference._teams) == 0

    @mock.patch('requests.get', side_effect=mock_pyquery)
    @mock.patch('requests.head', side_effect=mock_request)
    def test_invalid_default_year_reverts_to_previous_year(self,
                                                           *args,
                                                           **kwargs):
        flexmock(utils) \
            .should_receive('_find_year_for_season') \
            .and_return(2019)

        conferences = Conferences()

        assert conferences.team_conference == self.team_conference
        assert conferences.conferences == self.conferences_result

    @mock.patch('requests.get', side_effect=mock_pyquery)
    @mock.patch('requests.head', side_effect=mock_request)
    def test_invalid_conference_year_reverts_to_previous_year(self,
                                                              *args,
                                                              **kwargs):
        flexmock(utils) \
            .should_receive('_find_year_for_season') \
            .and_return(2019)

        conference = Conference('big-12')

        assert len(conference._teams) == 10
