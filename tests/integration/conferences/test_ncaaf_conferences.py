import mock
import pytest
from flexmock import flexmock
from os.path import join, dirname
from sportsreference import utils
from sportsreference.ncaaf.conferences import Conference, Conferences


YEAR = 2018


def read_file(filename):
    filepath = join(dirname(__file__), 'ncaaf', filename)
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
    if 'acc' in url:
        html_contents = read_file('%s-acc.html' % YEAR)
        return MockPQ(html_contents)
    if 'sec' in url:
        html_contents = read_file('%s-sec.html' % YEAR)
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


class TestNCAAFConferences:
    def setup_method(self):
        team_conference = {'florida-state': 'acc',
                           'boston-college': 'acc',
                           'clemson': 'acc',
                           'north-carolina-state': 'acc',
                           'syracuse': 'acc',
                           'wake-forest': 'acc',
                           'louisville': 'acc',
                           'virginia-tech': 'acc',
                           'duke': 'acc',
                           'georgia-tech': 'acc',
                           'pittsburgh': 'acc',
                           'virginia': 'acc',
                           'miami-fl': 'acc',
                           'north-carolina': 'acc',
                           'florida': 'sec',
                           'georgia': 'sec',
                           'kentucky': 'sec',
                           'missouri': 'sec',
                           'south-carolina': 'sec',
                           'vanderbilt': 'sec',
                           'tennessee': 'sec',
                           'alabama': 'sec',
                           'arkansas': 'sec',
                           'auburn': 'sec',
                           'louisiana-state': 'sec',
                           'mississippi-state': 'sec',
                           'mississippi': 'sec',
                           'texas-am': 'sec'}
        conferences_result = {'acc': {
                                  'name': 'Atlantic Coast Conference',
                                  'teams': {'florida-state': 'Florida State',
                                            'boston-college': 'Boston College',
                                            'clemson': 'Clemson',
                                            'north-carolina-state':
                                            'North Carolina State',
                                            'syracuse': 'Syracuse',
                                            'wake-forest': 'Wake Forest',
                                            'louisville': 'Louisville',
                                            'virginia-tech': 'Virginia Tech',
                                            'duke': 'Duke',
                                            'georgia-tech': 'Georgia Tech',
                                            'pittsburgh': 'Pitt',
                                            'virginia': 'Virginia',
                                            'miami-fl': 'Miami (FL)',
                                            'north-carolina': 'North Carolina'}
                                    },
                              'sec': {
                                    'name': 'Southeastern Conference',
                                    'teams': {'florida': 'Florida',
                                              'georgia': 'Georgia',
                                              'kentucky': 'Kentucky',
                                              'missouri': 'Missouri',
                                              'south-carolina':
                                              'South Carolina',
                                              'vanderbilt': 'Vanderbilt',
                                              'tennessee': 'Tennessee',
                                              'alabama': 'Alabama',
                                              'arkansas': 'Arkansas',
                                              'auburn': 'Auburn',
                                              'louisiana-state': 'LSU',
                                              'mississippi-state':
                                              'Mississippi State',
                                              'mississippi': 'Ole Miss',
                                              'texas-am': 'Texas A&M'}
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

        conference = Conference('acc')

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

        conference = Conference('acc')

        assert len(conference._teams) == 14

    @mock.patch('requests.get', side_effect=mock_pyquery)
    @mock.patch('requests.head', side_effect=mock_request)
    def test_invalid_conference_page_skips_error(self, *args, **kwargs):
        conference = Conference('BAD', ignore_missing=True)
