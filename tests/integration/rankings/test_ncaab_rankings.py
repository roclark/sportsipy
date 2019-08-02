import mock
import pytest
from flexmock import flexmock
from os.path import join, dirname
from sportsreference import utils
from sportsreference.ncaab.rankings import Rankings


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
    html_contents = read_file('%s-polls.html' % YEAR)
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


class TestNCAABRankings:
    def setup_method(self):
        results_extended = [
            {
                'abbreviation': 'virginia',
                'name': 'Virginia',
                'rank': 1,
                'week': 19,
                'date': 'Final',
                'previous': '1',
                'change': 0
            },
            {
                'abbreviation': 'villanova',
                'name': 'Villanova',
                'rank': 2,
                'week': 19,
                'date': 'Final',
                'previous': '2',
                'change': 0
            },
            {
                'abbreviation': 'xavier',
                'name': 'Xavier',
                'rank': 3,
                'week': 19,
                'date': 'Final',
                'previous': '3',
                'change': 0
            },
            {
                'abbreviation': 'kansas',
                'name': 'Kansas',
                'rank': 4,
                'week': 19,
                'date': 'Final',
                'previous': '9',
                'change': 5
            },
            {
                'abbreviation': 'michigan-state',
                'name': 'Michigan State',
                'rank': 5,
                'week': 19,
                'date': 'Final',
                'previous': '4',
                'change': -1
            },
            {
                'abbreviation': 'cincinnati',
                'name': 'Cincinnati',
                'rank': 6,
                'week': 19,
                'date': 'Final',
                'previous': '8',
                'change': 2
            },
            {
                'abbreviation': 'michigan',
                'name': 'Michigan',
                'rank': 7,
                'week': 19,
                'date': 'Final',
                'previous': '7',
                'change': 0
            },
            {
                'abbreviation': 'gonzaga',
                'name': 'Gonzaga',
                'rank': 8,
                'week': 19,
                'date': 'Final',
                'previous': '6',
                'change': -2
            },
            {
                'abbreviation': 'duke',
                'name': 'Duke',
                'rank': 9,
                'week': 19,
                'date': 'Final',
                'previous': '5',
                'change': -4
            },
            {
                'abbreviation': 'north-carolina',
                'name': 'North Carolina',
                'rank': 10,
                'week': 19,
                'date': 'Final',
                'previous': '12',
                'change': 2
            },
            {
                'abbreviation': 'purdue',
                'name': 'Purdue',
                'rank': 11,
                'week': 19,
                'date': 'Final',
                'previous': '10',
                'change': -1
            },
            {
                'abbreviation': 'arizona',
                'name': 'Arizona',
                'rank': 12,
                'week': 19,
                'date': 'Final',
                'previous': '15',
                'change': 3
            },
            {
                'abbreviation': 'tennessee',
                'name': 'Tennessee',
                'rank': 13,
                'week': 19,
                'date': 'Final',
                'previous': '13',
                'change': 0
            },
            {
                'abbreviation': 'texas-tech',
                'name': 'Texas Tech',
                'rank': 14,
                'week': 19,
                'date': 'Final',
                'previous': '14',
                'change': 0
            },
            {
                'abbreviation': 'west-virginia',
                'name': 'West Virginia',
                'rank': 15,
                'week': 19,
                'date': 'Final',
                'previous': '18',
                'change': 3
            },
            {
                'abbreviation': 'wichita-state',
                'name': 'Wichita State',
                'rank': 16,
                'week': 19,
                'date': 'Final',
                'previous': '11',
                'change': -5
            },
            {
                'abbreviation': 'ohio-state',
                'name': 'Ohio State',
                'rank': 17,
                'week': 19,
                'date': 'Final',
                'previous': '17',
                'change': 0
            },
            {
                'abbreviation': 'kentucky',
                'name': 'Kentucky',
                'rank': 18,
                'week': 19,
                'date': 'Final',
                'previous': '',
                'change': 0
            },
            {
                'abbreviation': 'auburn',
                'name': 'Auburn',
                'rank': 19,
                'week': 19,
                'date': 'Final',
                'previous': '16',
                'change': -3
            },
            {
                'abbreviation': 'clemson',
                'name': 'Clemson',
                'rank': 20,
                'week': 19,
                'date': 'Final',
                'previous': '19',
                'change': -1
            },
            {
                'abbreviation': 'houston',
                'name': 'Houston',
                'rank': 21,
                'week': 19,
                'date': 'Final',
                'previous': '21',
                'change': 0
            },
            {
                'abbreviation': 'miami-fl',
                'name': 'Miami (FL)',
                'rank': 22,
                'week': 19,
                'date': 'Final',
                'previous': '24',
                'change': 2
            },
            {
                'abbreviation': 'florida',
                'name': 'Florida',
                'rank': 23,
                'week': 19,
                'date': 'Final',
                'previous': '23',
                'change': 0
            },
            {
                'abbreviation': 'nevada',
                'name': 'Nevada',
                'rank': 24,
                'week': 19,
                'date': 'Final',
                'previous': '22',
                'change': -2
            },
            {
                'abbreviation': 'saint-marys-ca',
                'name': "Saint Mary's (CA)",
                'rank': 25,
                'week': 19,
                'date': 'Final',
                'previous': '20',
                'change': -5
            }
        ]
        results = {
            'virginia': 1,
            'villanova': 2,
            'xavier': 3,
            'kansas': 4,
            'michigan-state': 5,
            'cincinnati': 6,
            'michigan': 7,
            'gonzaga': 8,
            'duke': 9,
            'north-carolina': 10,
            'purdue': 11,
            'arizona': 12,
            'tennessee': 13,
            'texas-tech': 14,
            'west-virginia': 15,
            'wichita-state': 16,
            'ohio-state': 17,
            'kentucky': 18,
            'auburn': 19,
            'clemson': 20,
            'houston': 21,
            'miami-fl': 22,
            'florida': 23,
            'nevada': 24,
            'saint-marys-ca': 25
        }
        results_complete = {19: [
            {'abbreviation': 'virginia',
             'name': 'Virginia',
             'rank': 1,
             'week': 19,
             'date': 'Final',
             'previous': '1',
             'change': 0},
            {'abbreviation': 'villanova',
             'name': 'Villanova',
             'rank': 2,
             'week': 19,
             'date': 'Final',
             'previous': '2',
             'change': 0},
            {'abbreviation': 'xavier',
             'name': 'Xavier',
             'rank': 3,
             'week': 19,
             'date': 'Final',
             'previous': '3',
             'change': 0},
            {'abbreviation': 'kansas',
             'name': 'Kansas',
             'rank': 4,
             'week': 19,
             'date': 'Final',
             'previous': '9',
             'change': 5},
            {'abbreviation': 'michigan-state',
             'name': 'Michigan State',
             'rank': 5,
             'week': 19,
             'date': 'Final',
             'previous': '4',
             'change': -1},
            {'abbreviation': 'cincinnati',
             'name': 'Cincinnati',
             'rank': 6,
             'week': 19,
             'date': 'Final',
             'previous': '8',
             'change': 2},
            {'abbreviation': 'michigan',
             'name': 'Michigan',
             'rank': 7,
             'week': 19,
             'date': 'Final',
             'previous': '7',
             'change': 0},
            {'abbreviation': 'gonzaga',
             'name': 'Gonzaga',
             'rank': 8,
             'week': 19,
             'date': 'Final',
             'previous': '6',
             'change': -2},
            {'abbreviation': 'duke',
             'name': 'Duke',
             'rank': 9,
             'week': 19,
             'date': 'Final',
             'previous': '5',
             'change': -4},
            {'abbreviation': 'north-carolina',
             'name': 'North Carolina',
             'rank': 10,
             'week': 19,
             'date': 'Final',
             'previous': '12',
             'change': 2},
            {'abbreviation': 'purdue',
             'name': 'Purdue',
             'rank': 11,
             'week': 19,
             'date': 'Final',
             'previous': '10',
             'change': -1},
            {'abbreviation': 'arizona',
             'name': 'Arizona',
             'rank': 12,
             'week': 19,
             'date': 'Final',
             'previous': '15',
             'change': 3},
            {'abbreviation': 'tennessee',
             'name': 'Tennessee',
             'rank': 13,
             'week': 19,
             'date': 'Final',
             'previous': '13',
             'change': 0},
            {'abbreviation': 'texas-tech',
             'name': 'Texas Tech',
             'rank': 14,
             'week': 19,
             'date': 'Final',
             'previous': '14',
             'change': 0},
            {'abbreviation': 'west-virginia',
             'name': 'West Virginia',
             'rank': 15,
             'week': 19,
             'date': 'Final',
             'previous': '18',
             'change': 3},
            {'abbreviation': 'wichita-state',
             'name': 'Wichita State',
             'rank': 16,
             'week': 19,
             'date': 'Final',
             'previous': '11',
             'change': -5},
            {'abbreviation': 'ohio-state',
             'name': 'Ohio State',
             'rank': 17,
             'week': 19,
             'date': 'Final',
             'previous': '17',
             'change': 0},
            {'abbreviation': 'kentucky',
             'name': 'Kentucky',
             'rank': 18,
             'week': 19,
             'date': 'Final',
             'previous': '',
             'change': 0},
            {'abbreviation': 'auburn',
             'name': 'Auburn',
             'rank': 19,
             'week': 19,
             'date': 'Final',
             'previous': '16',
             'change': -3},
            {'abbreviation': 'clemson',
             'name': 'Clemson',
             'rank': 20,
             'week': 19,
             'date': 'Final',
             'previous': '19',
             'change': -1},
            {'abbreviation': 'houston',
             'name': 'Houston',
             'rank': 21,
             'week': 19,
             'date': 'Final',
             'previous': '21',
             'change': 0},
            {'abbreviation': 'miami-fl',
             'name': 'Miami (FL)',
             'rank': 22,
             'week': 19,
             'date': 'Final',
             'previous': '24',
             'change': 2},
            {'abbreviation': 'florida',
             'name': 'Florida',
             'rank': 23,
             'week': 19,
             'date': 'Final',
             'previous': '23',
             'change': 0},
            {'abbreviation': 'nevada',
             'name': 'Nevada',
             'rank': 24,
             'week': 19,
             'date': 'Final',
             'previous': '22',
             'change': -2},
            {'abbreviation': 'saint-marys-ca',
             'name': "Saint Mary's (CA)",
             'rank': 25,
             'week': 19,
             'date': 'Final',
             'previous': '20',
             'change': -5}
            ],
            18: [
            {'abbreviation': 'virginia',
             'name': 'Virginia',
             'rank': 1,
             'week': 18,
             'date': '2018-03-05',
             'previous': '1',
             'change': 0},
            {'abbreviation': 'villanova',
             'name': 'Villanova',
             'rank': 2,
             'week': 18,
             'date': '2018-03-05',
             'previous': '4',
             'change': 2},
            {'abbreviation': 'xavier',
             'name': 'Xavier',
             'rank': 3,
             'week': 18,
             'date': '2018-03-05',
             'previous': '3',
             'change': 0},
            {'abbreviation': 'michigan-state',
             'name': 'Michigan State',
             'rank': 4,
             'week': 18,
             'date': '2018-03-05',
             'previous': '2',
             'change': -2},
            {'abbreviation': 'duke',
             'name': 'Duke',
             'rank': 5,
             'week': 18,
             'date': '2018-03-05',
             'previous': '5',
             'change': 0},
            {'abbreviation': 'gonzaga',
             'name': 'Gonzaga',
             'rank': 6,
             'week': 18,
             'date': '2018-03-05',
             'previous': '7',
             'change': 1},
            {'abbreviation': 'michigan',
             'name': 'Michigan',
             'rank': 7,
             'week': 18,
             'date': '2018-03-05',
             'previous': '15',
             'change': 8},
            {'abbreviation': 'cincinnati',
             'name': 'Cincinnati',
             'rank': 8,
             'week': 18,
             'date': '2018-03-05',
             'previous': '10',
             'change': 2},
            {'abbreviation': 'kansas',
             'name': 'Kansas',
             'rank': 9,
             'week': 18,
             'date': '2018-03-05',
             'previous': '6',
             'change': -3},
            {'abbreviation': 'purdue',
             'name': 'Purdue',
             'rank': 10,
             'week': 18,
             'date': '2018-03-05',
             'previous': '8',
             'change': -2},
            {'abbreviation': 'wichita-state',
             'name': 'Wichita State',
             'rank': 11,
             'week': 18,
             'date': '2018-03-05',
             'previous': '11',
             'change': 0},
            {'abbreviation': 'north-carolina',
             'name': 'North Carolina',
             'rank': 12,
             'week': 18,
             'date': '2018-03-05',
             'previous': '9',
             'change': -3},
            {'abbreviation': 'tennessee',
             'name': 'Tennessee',
             'rank': 13,
             'week': 18,
             'date': '2018-03-05',
             'previous': '16',
             'change': 3},
            {'abbreviation': 'texas-tech',
             'name': 'Texas Tech',
             'rank': 14,
             'week': 18,
             'date': '2018-03-05',
             'previous': '12',
             'change': -2},
            {'abbreviation': 'arizona',
             'name': 'Arizona',
             'rank': 15,
             'week': 18,
             'date': '2018-03-05',
             'previous': '19',
             'change': 4},
            {'abbreviation': 'auburn',
             'name': 'Auburn',
             'rank': 16,
             'week': 18,
             'date': '2018-03-05',
             'previous': '14',
             'change': -2},
            {'abbreviation': 'ohio-state',
             'name': 'Ohio State',
             'rank': 17,
             'week': 18,
             'date': '2018-03-05',
             'previous': '13',
             'change': -4},
            {'abbreviation': 'west-virginia',
             'name': 'West Virginia',
             'rank': 18,
             'week': 18,
             'date': '2018-03-05',
             'previous': '20',
             'change': 2},
            {'abbreviation': 'clemson',
             'name': 'Clemson',
             'rank': 19,
             'week': 18,
             'date': '2018-03-05',
             'previous': '18',
             'change': -1},
            {'abbreviation': 'saint-marys-ca',
             'name': "Saint Mary's (CA)",
             'rank': 20,
             'week': 18,
             'date': '2018-03-05',
             'previous': '22',
             'change': 2},
            {'abbreviation': 'houston',
             'name': 'Houston',
             'rank': 21,
             'week': 18,
             'date': '2018-03-05',
             'previous': '25',
             'change': 4},
            {'abbreviation': 'nevada',
             'name': 'Nevada',
             'rank': 22,
             'week': 18,
             'date': '2018-03-05',
             'previous': '21',
             'change': -1},
            {'abbreviation': 'florida',
             'name': 'Florida',
             'rank': 23,
             'week': 18,
             'date': '2018-03-05',
             'previous': '',
             'change': 0},
            {'abbreviation': 'miami-fl',
             'name': 'Miami (FL)',
             'rank': 24,
             'week': 18,
             'date': '2018-03-05',
             'previous': '',
             'change': 0},
            {'abbreviation': 'rhode-island',
             'name': 'Rhode Island',
             'rank': 25,
             'week': 18,
             'date': '2018-03-05',
             'previous': '17',
             'change': -8}
            ]}
        self.results_extended = results_extended
        self.results = results
        self.results_complete = results_complete

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_rankings_integration(self, *args, **kwargs):
        flexmock(utils) \
            .should_receive('_find_year_for_season') \
            .and_return(YEAR)

        rankings = Rankings()

        assert rankings.current_extended == self.results_extended
        assert rankings.current == self.results
        assert rankings.complete == self.results_complete

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_rankings_integration_bad_url(self, *args, **kwargs):
        with pytest.raises(ValueError):
            rankings = Rankings('BAD')

    @mock.patch('requests.get', side_effect=mock_pyquery)
    @mock.patch('requests.head', side_effect=mock_request)
    def test_invalid_default_year_reverts_to_previous_year(self,
                                                           *args,
                                                           **kwargs):
        flexmock(utils) \
            .should_receive('_find_year_for_season') \
            .and_return(2019)

        rankings = Rankings()

        assert rankings.current_extended == self.results_extended
        assert rankings.current == self.results
        assert rankings.complete == self.results_complete
