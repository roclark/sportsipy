import mock
import pytest
from flexmock import flexmock
from os.path import join, dirname
from sportsreference import utils
from sportsreference.ncaaf.rankings import Rankings


YEAR = 2017


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


class TestNCAAFRankings:
    def setup_method(self):
        results_extended = [
            {
                'abbreviation': 'alabama',
                'name': 'Alabama',
                'rank': 1,
                'week': 16,
                'date': 'Final',
                'previous': '4',
                'change': 3
            },
            {
                'abbreviation': 'georgia',
                'name': 'Georgia',
                'rank': 2,
                'week': 16,
                'date': 'Final',
                'previous': '3',
                'change': 1
            },
            {
                'abbreviation': 'oklahoma',
                'name': 'Oklahoma',
                'rank': 3,
                'week': 16,
                'date': 'Final',
                'previous': '2',
                'change': -1
            },
            {
                'abbreviation': 'clemson',
                'name': 'Clemson',
                'rank': 4,
                'week': 16,
                'date': 'Final',
                'previous': '1',
                'change': -3
            },
            {
                'abbreviation': 'ohio-state',
                'name': 'Ohio State',
                'rank': 5,
                'week': 16,
                'date': 'Final',
                'previous': '5',
                'change': 0
            },
            {
                'abbreviation': 'central-florida',
                'name': 'UCF',
                'rank': 6,
                'week': 16,
                'date': 'Final',
                'previous': '10',
                'change': 4
            },
            {
                'abbreviation': 'wisconsin',
                'name': 'Wisconsin',
                'rank': 7,
                'week': 16,
                'date': 'Final',
                'previous': '6',
                'change': -1
            },
            {
                'abbreviation': 'penn-state',
                'name': 'Penn State',
                'rank': 8,
                'week': 16,
                'date': 'Final',
                'previous': '9',
                'change': 1
            },
            {
                'abbreviation': 'texas-christian',
                'name': 'Texas Christian',
                'rank': 9,
                'week': 16,
                'date': 'Final',
                'previous': '13',
                'change': 4
            },
            {
                'abbreviation': 'auburn',
                'name': 'Auburn',
                'rank': 10,
                'week': 16,
                'date': 'Final',
                'previous': '7',
                'change': -3
            },
            {
                'abbreviation': 'notre-dame',
                'name': 'Notre Dame',
                'rank': 11,
                'week': 16,
                'date': 'Final',
                'previous': '14',
                'change': 3
            },
            {
                'abbreviation': 'southern-california',
                'name': 'USC',
                'rank': 12,
                'week': 16,
                'date': 'Final',
                'previous': '8',
                'change': -4
            },
            {
                'abbreviation': 'miami-fl',
                'name': 'Miami (FL)',
                'rank': 13,
                'week': 16,
                'date': 'Final',
                'previous': '11',
                'change': -2
            },
            {
                'abbreviation': 'oklahoma-state',
                'name': 'Oklahoma State',
                'rank': 14,
                'week': 16,
                'date': 'Final',
                'previous': '17',
                'change': 3
            },
            {
                'abbreviation': 'michigan-state',
                'name': 'Michigan State',
                'rank': 15,
                'week': 16,
                'date': 'Final',
                'previous': '18',
                'change': 3
            },
            {
                'abbreviation': 'washington',
                'name': 'Washington',
                'rank': 16,
                'week': 16,
                'date': 'Final',
                'previous': '12',
                'change': -4
            },
            {
                'abbreviation': 'northwestern',
                'name': 'Northwestern',
                'rank': 17,
                'week': 16,
                'date': 'Final',
                'previous': '20',
                'change': 3
            },
            {
                'abbreviation': 'louisiana-state',
                'name': 'LSU',
                'rank': 18,
                'week': 16,
                'date': 'Final',
                'previous': '16',
                'change': -2
            },
            {
                'abbreviation': 'mississippi-state',
                'name': 'Mississippi State',
                'rank': 19,
                'week': 16,
                'date': 'Final',
                'previous': '24',
                'change': 5
            },
            {
                'abbreviation': 'stanford',
                'name': 'Stanford',
                'rank': 20,
                'week': 16,
                'date': 'Final',
                'previous': '15',
                'change': -5
            },
            {
                'abbreviation': 'south-florida',
                'name': 'South Florida',
                'rank': 21,
                'week': 16,
                'date': 'Final',
                'previous': '23',
                'change': 2
            },
            {
                'abbreviation': 'boise-state',
                'name': 'Boise State',
                'rank': 22,
                'week': 16,
                'date': 'Final',
                'previous': '25',
                'change': 3
            },
            {
                'abbreviation': 'north-carolina-state',
                'name': 'North Carolina State',
                'rank': 23,
                'week': 16,
                'date': 'Final',
                'previous': '',
                'change': 0
            },
            {
                'abbreviation': 'virginia-tech',
                'name': 'Virginia Tech',
                'rank': 24,
                'week': 16,
                'date': 'Final',
                'previous': '22',
                'change': -2
            },
            {
                'abbreviation': 'memphis',
                'name': 'Memphis',
                'rank': 25,
                'week': 16,
                'date': 'Final',
                'previous': '19',
                'change': -6
            }
        ]
        results = {
            'alabama': 1,
            'georgia': 2,
            'oklahoma': 3,
            'clemson': 4,
            'ohio-state': 5,
            'central-florida': 6,
            'wisconsin': 7,
            'penn-state': 8,
            'texas-christian': 9,
            'auburn': 10,
            'notre-dame': 11,
            'southern-california': 12,
            'miami-fl': 13,
            'oklahoma-state': 14,
            'michigan-state': 15,
            'washington': 16,
            'northwestern': 17,
            'louisiana-state': 18,
            'mississippi-state': 19,
            'stanford': 20,
            'south-florida': 21,
            'boise-state': 22,
            'north-carolina-state': 23,
            'virginia-tech': 24,
            'memphis': 25
        }
        results_complete = {16: [
            {'abbreviation': 'alabama',
             'name': 'Alabama',
             'rank': 1,
             'week': 16,
             'date': 'Final',
             'previous': '4',
             'change': 3},
            {'abbreviation': 'georgia',
             'name': 'Georgia',
             'rank': 2,
             'week': 16,
             'date': 'Final',
             'previous': '3',
             'change': 1},
            {'abbreviation': 'oklahoma',
             'name': 'Oklahoma',
             'rank': 3,
             'week': 16,
             'date': 'Final',
             'previous': '2',
             'change': -1},
            {'abbreviation': 'clemson',
             'name': 'Clemson',
             'rank': 4,
             'week': 16,
             'date': 'Final',
             'previous': '1',
             'change': -3},
            {'abbreviation': 'ohio-state',
             'name': 'Ohio State',
             'rank': 5,
             'week': 16,
             'date': 'Final',
             'previous': '5',
             'change': 0},
            {'abbreviation': 'central-florida',
             'name': 'UCF',
             'rank': 6,
             'week': 16,
             'date': 'Final',
             'previous': '10',
             'change': 4},
            {'abbreviation': 'wisconsin',
             'name': 'Wisconsin',
             'rank': 7,
             'week': 16,
             'date': 'Final',
             'previous': '6',
             'change': -1},
            {'abbreviation': 'penn-state',
             'name': 'Penn State',
             'rank': 8,
             'week': 16,
             'date': 'Final',
             'previous': '9',
             'change': 1},
            {'abbreviation': 'texas-christian',
             'name': 'Texas Christian',
             'rank': 9,
             'week': 16,
             'date': 'Final',
             'previous': '13',
             'change': 4},
            {'abbreviation': 'auburn',
             'name': 'Auburn',
             'rank': 10,
             'week': 16,
             'date': 'Final',
             'previous': '7',
             'change': -3},
            {'abbreviation': 'notre-dame',
             'name': 'Notre Dame',
             'rank': 11,
             'week': 16,
             'date': 'Final',
             'previous': '14',
             'change': 3},
            {'abbreviation': 'southern-california',
             'name': 'USC',
             'rank': 12,
             'week': 16,
             'date': 'Final',
             'previous': '8',
             'change': -4},
            {'abbreviation': 'miami-fl',
             'name': 'Miami (FL)',
             'rank': 13,
             'week': 16,
             'date': 'Final',
             'previous': '11',
             'change': -2},
            {'abbreviation': 'oklahoma-state',
             'name': 'Oklahoma State',
             'rank': 14,
             'week': 16,
             'date': 'Final',
             'previous': '17',
             'change': 3},
            {'abbreviation': 'michigan-state',
             'name': 'Michigan State',
             'rank': 15,
             'week': 16,
             'date': 'Final',
             'previous': '18',
             'change': 3},
            {'abbreviation': 'washington',
             'name': 'Washington',
             'rank': 16,
             'week': 16,
             'date': 'Final',
             'previous': '12',
             'change': -4},
            {'abbreviation': 'northwestern',
             'name': 'Northwestern',
             'rank': 17,
             'week': 16,
             'date': 'Final',
             'previous': '20',
             'change': 3},
            {'abbreviation': 'louisiana-state',
             'name': 'LSU',
             'rank': 18,
             'week': 16,
             'date': 'Final',
             'previous': '16',
             'change': -2},
            {'abbreviation': 'mississippi-state',
             'name': 'Mississippi State',
             'rank': 19,
             'week': 16,
             'date': 'Final',
             'previous': '24',
             'change': 5},
            {'abbreviation': 'stanford',
             'name': 'Stanford',
             'rank': 20,
             'week': 16,
             'date': 'Final',
             'previous': '15',
             'change': -5},
            {'abbreviation': 'south-florida',
             'name': 'South Florida',
             'rank': 21,
             'week': 16,
             'date': 'Final',
             'previous': '23',
             'change': 2},
            {'abbreviation': 'boise-state',
             'name': 'Boise State',
             'rank': 22,
             'week': 16,
             'date': 'Final',
             'previous': '25',
             'change': 3},
            {'abbreviation': 'north-carolina-state',
             'name': 'North Carolina State',
             'rank': 23,
             'week': 16,
             'date': 'Final',
             'previous': '',
             'change': 0},
            {'abbreviation': 'virginia-tech',
             'name': 'Virginia Tech',
             'rank': 24,
             'week': 16,
             'date': 'Final',
             'previous': '22',
             'change': -2},
            {'abbreviation': 'memphis',
             'name': 'Memphis',
             'rank': 25,
             'week': 16,
             'date': 'Final',
             'previous': '19',
             'change': -6}
            ],
            15: [
            {'abbreviation': 'clemson',
             'name': 'Clemson',
             'rank': 1,
             'week': 15,
             'date': '2017-12-03',
             'previous': '1',
             'change': 0},
            {'abbreviation': 'oklahoma',
             'name': 'Oklahoma',
             'rank': 2,
             'week': 15,
             'date': '2017-12-03',
             'previous': '2',
             'change': 0},
            {'abbreviation': 'georgia',
             'name': 'Georgia',
             'rank': 3,
             'week': 15,
             'date': '2017-12-03',
             'previous': '6',
             'change': 3},
            {'abbreviation': 'alabama',
             'name': 'Alabama',
             'rank': 4,
             'week': 15,
             'date': '2017-12-03',
             'previous': '5',
             'change': 1},
            {'abbreviation': 'ohio-state',
             'name': 'Ohio State',
             'rank': 5,
             'week': 15,
             'date': '2017-12-03',
             'previous': '8',
             'change': 3},
            {'abbreviation': 'wisconsin',
             'name': 'Wisconsin',
             'rank': 6,
             'week': 15,
             'date': '2017-12-03',
             'previous': '3',
             'change': -3},
            {'abbreviation': 'auburn',
             'name': 'Auburn',
             'rank': 7,
             'week': 15,
             'date': '2017-12-03',
             'previous': '4',
             'change': -3},
            {'abbreviation': 'southern-california',
             'name': 'USC',
             'rank': 8,
             'week': 15,
             'date': '2017-12-03',
             'previous': '11',
             'change': 3},
            {'abbreviation': 'penn-state',
             'name': 'Penn State',
             'rank': 9,
             'week': 15,
             'date': '2017-12-03',
             'previous': '9',
             'change': 0},
            {'abbreviation': 'central-florida',
             'name': 'UCF',
             'rank': 10,
             'week': 15,
             'date': '2017-12-03',
             'previous': '12',
             'change': 2},
            {'abbreviation': 'miami-fl',
             'name': 'Miami (FL)',
             'rank': 11,
             'week': 15,
             'date': '2017-12-03',
             'previous': '7',
             'change': -4},
            {'abbreviation': 'washington',
             'name': 'Washington',
             'rank': 12,
             'week': 15,
             'date': '2017-12-03',
             'previous': '13',
             'change': 1},
            {'abbreviation': 'texas-christian',
             'name': 'Texas Christian',
             'rank': 13,
             'week': 15,
             'date': '2017-12-03',
             'previous': '10',
             'change': -3},
            {'abbreviation': 'notre-dame',
             'name': 'Notre Dame',
             'rank': 14,
             'week': 15,
             'date': '2017-12-03',
             'previous': '15',
             'change': 1},
            {'abbreviation': 'stanford',
             'name': 'Stanford',
             'rank': 15,
             'week': 15,
             'date': '2017-12-03',
             'previous': '14',
             'change': -1},
            {'abbreviation': 'louisiana-state',
             'name': 'LSU',
             'rank': 16,
             'week': 15,
             'date': '2017-12-03',
             'previous': '17',
             'change': 1},
            {'abbreviation': 'oklahoma-state',
             'name': 'Oklahoma State',
             'rank': 17,
             'week': 15,
             'date': '2017-12-03',
             'previous': '18',
             'change': 1},
            {'abbreviation': 'michigan-state',
             'name': 'Michigan State',
             'rank': 18,
             'week': 15,
             'date': '2017-12-03',
             'previous': '19',
             'change': 1},
            {'abbreviation': 'memphis',
             'name': 'Memphis',
             'rank': 19,
             'week': 15,
             'date': '2017-12-03',
             'previous': '16',
             'change': -3},
            {'abbreviation': 'northwestern',
             'name': 'Northwestern',
             'rank': 20,
             'week': 15,
             'date': '2017-12-03',
             'previous': '20',
             'change': 0},
            {'abbreviation': 'washington-state',
             'name': 'Washington State',
             'rank': 21,
             'week': 15,
             'date': '2017-12-03',
             'previous': '21',
             'change': 0},
            {'abbreviation': 'virginia-tech',
             'name': 'Virginia Tech',
             'rank': 22,
             'week': 15,
             'date': '2017-12-03',
             'previous': '22',
             'change': 0},
            {'abbreviation': 'south-florida',
             'name': 'South Florida',
             'rank': 23,
             'week': 15,
             'date': '2017-12-03',
             'previous': '23',
             'change': 0},
            {'abbreviation': 'mississippi-state',
             'name': 'Mississippi State',
             'rank': 24,
             'week': 15,
             'date': '2017-12-03',
             'previous': '24',
             'change': 0},
            {'abbreviation': 'boise-state',
             'name': 'Boise State',
             'rank': 25,
             'week': 15,
             'date': '2017-12-03',
             'previous': '',
             'change': 0}
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
            .and_return(2018)

        rankings = Rankings()

        assert rankings.current_extended == self.results_extended
        assert rankings.current == self.results
        assert rankings.complete == self.results_complete
