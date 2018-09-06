from flexmock import flexmock
from sportsreference import utils


class SeasonStarts:
    def __init__(self, league, month, expected_year):
        self.league = league
        self.month = month
        self.expected_year = expected_year


class MockDateTime:
    def __init__(self, month, year):
        self.month = month
        self.year = year


class Item:
    def __init__(self, input_string):
        self.input_string = input_string

    def text(self):
        return self.input_string


class Html:
    def __init__(self, html_string, item_list):
        self.html_string = html_string
        self.item_list = item_list

    def attr(self, attribute):
        return self.html_string

    def items(self):
        items = []
        for item in self.item_list:
            items.append(Item(item))
        return items


class MockHtml:
    def __init__(self, html_string, item_list):
        self.html_string = html_string
        self.item_list = item_list

    def __call__(self, tag):
        return Html(self.html_string, self.item_list)


class TestUtils:
    def test__find_year_for_season_returns_correct_year(self):
        season_start_matrix = [
            # MLB Months
            SeasonStarts('mlb', 1, 2017),
            SeasonStarts('mlb', 2, 2017),
            SeasonStarts('mlb', 3, 2018),
            SeasonStarts('mlb', 4, 2018),
            SeasonStarts('mlb', 5, 2018),
            SeasonStarts('mlb', 6, 2018),
            SeasonStarts('mlb', 7, 2018),
            SeasonStarts('mlb', 8, 2018),
            SeasonStarts('mlb', 9, 2018),
            SeasonStarts('mlb', 10, 2018),
            SeasonStarts('mlb', 11, 2018),
            SeasonStarts('mlb', 12, 2018),
            # NBA Months
            SeasonStarts('nba', 1, 2018),
            SeasonStarts('nba', 2, 2018),
            SeasonStarts('nba', 3, 2018),
            SeasonStarts('nba', 4, 2018),
            SeasonStarts('nba', 5, 2018),
            SeasonStarts('nba', 6, 2018),
            SeasonStarts('nba', 7, 2018),
            SeasonStarts('nba', 8, 2018),
            SeasonStarts('nba', 9, 2019),
            SeasonStarts('nba', 10, 2019),
            SeasonStarts('nba', 11, 2019),
            SeasonStarts('nba', 12, 2019),
            # NCAAB Months
            SeasonStarts('ncaab', 1, 2018),
            SeasonStarts('ncaab', 2, 2018),
            SeasonStarts('ncaab', 3, 2018),
            SeasonStarts('ncaab', 4, 2018),
            SeasonStarts('ncaab', 5, 2018),
            SeasonStarts('ncaab', 6, 2018),
            SeasonStarts('ncaab', 7, 2018),
            SeasonStarts('ncaab', 8, 2018),
            SeasonStarts('ncaab', 9, 2018),
            SeasonStarts('ncaab', 10, 2019),
            SeasonStarts('ncaab', 11, 2019),
            SeasonStarts('ncaab', 12, 2019),
            # NCAAF Months
            SeasonStarts('ncaaf', 1, 2017),
            SeasonStarts('ncaaf', 2, 2017),
            SeasonStarts('ncaaf', 3, 2017),
            SeasonStarts('ncaaf', 4, 2017),
            SeasonStarts('ncaaf', 5, 2017),
            SeasonStarts('ncaaf', 6, 2017),
            SeasonStarts('ncaaf', 7, 2018),
            SeasonStarts('ncaaf', 8, 2018),
            SeasonStarts('ncaaf', 9, 2018),
            SeasonStarts('ncaaf', 10, 2018),
            SeasonStarts('ncaaf', 11, 2018),
            SeasonStarts('ncaaf', 12, 2018),
            # NFL Months
            SeasonStarts('nfl', 1, 2017),
            SeasonStarts('nfl', 2, 2017),
            SeasonStarts('nfl', 3, 2017),
            SeasonStarts('nfl', 4, 2017),
            SeasonStarts('nfl', 5, 2017),
            SeasonStarts('nfl', 6, 2017),
            SeasonStarts('nfl', 7, 2017),
            SeasonStarts('nfl', 8, 2018),
            SeasonStarts('nfl', 9, 2018),
            SeasonStarts('nfl', 10, 2018),
            SeasonStarts('nfl', 11, 2018),
            SeasonStarts('nfl', 12, 2018),
            # NHL Months
            SeasonStarts('nhl', 1, 2018),
            SeasonStarts('nhl', 2, 2018),
            SeasonStarts('nhl', 3, 2018),
            SeasonStarts('nhl', 4, 2018),
            SeasonStarts('nhl', 5, 2018),
            SeasonStarts('nhl', 6, 2018),
            SeasonStarts('nhl', 7, 2018),
            SeasonStarts('nhl', 8, 2018),
            SeasonStarts('nhl', 9, 2019),
            SeasonStarts('nhl', 10, 2019),
            SeasonStarts('nhl', 11, 2019),
            SeasonStarts('nhl', 12, 2019)
        ]

        for month in season_start_matrix:
            mock_datetime = MockDateTime(month.month, 2018)
            flexmock(utils) \
                .should_receive('_todays_date')\
                .and_return(mock_datetime)

            result = utils._find_year_for_season(month.league)
            assert result == month.expected_year

    def test_remove_html_comment_tags_removes_comments(self):
        html_string = '''<html>
    <body>
        <!--<p>This should be kept.</p>-->
    </body>
</html>'''
        expected_output = '''<html>
    <body>
        <p>This should be kept.</p>
    </body>
</html>'''

        result = utils._remove_html_comment_tags(html_string)

        assert result == expected_output

    def test_remove_html_comment_tags_without_comments_doesnt_change(self):
        html_string = '''<html>
    <body>
        <p>This should be the same.</p>
    </body>
</html>'''
        expected_output = '''<html>
    <body>
        <p>This should be the same.</p>
    </body>
</html>'''

        result = utils._remove_html_comment_tags(html_string)

        assert result == expected_output

    def test_abbreviation_is_parsed_correctly(self):
        test_abbreviations = {'/teams/ARI/2018.shtml': 'ARI',
                              '/teams/nwe/2017.htm': 'NWE',
                              '/cfb/schools/clemson/2017.html': 'CLEMSON',
                              '/teams/GSW/2018.html': 'GSW',
                              '/cbb/schools/purdue/2018.html': 'PURDUE',
                              '/teams/TBL/2018.html': 'TBL'}

        for html, abbreviation in test_abbreviations.items():
            mock_html = MockHtml(html, None)
            result = utils._parse_abbreviation(mock_html)
            assert result == abbreviation

    def test__parse_field_returns_abbreviation(self):
        parsing_scheme = {'abbreviation': 'a'}
        input_abbreviation = '/teams/ARI/2018.shtml'
        expected = 'ARI'
        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return('ARI') \
            .once()

        result = utils._parse_field(parsing_scheme,
                                    MockHtml(input_abbreviation, None),
                                    'abbreviation')
        assert result == expected

    def test_parse_field_returns_none_on_index_error(self):
        parsing_scheme = {'batters_used': 'td[data-stat="batters_used"]:first'}
        html_string = '''<td class="right " data-stat="batters_used">32</td>
<td class="right " data-stat="age_bat">29.1</td>
<td class="right " data-stat="runs_per_game">4.10</td>'''
        expected = None

        result = utils._parse_field(parsing_scheme,
                                    MockHtml(html_string, [expected]),
                                    'batters_used',
                                    index=3)
        assert result == expected

    def test__parse_field_returns_value_for_non_abbreviation(self):
        parsing_scheme = {'batters_used': 'td[data-stat="batters_used"]:first'}
        html_string = '''<td class="right " data-stat="batters_used">32</td>
<td class="right " data-stat="age_bat">29.1</td>
<td class="right " data-stat="runs_per_game">4.10</td>'''
        expected = '32'

        result = utils._parse_field(parsing_scheme,
                                    MockHtml(html_string, [expected]),
                                    'batters_used')
        assert result == expected

    def test__get_stats_table_returns_correct_table(self):
        html_string = '''<div>
    <table class="stats_table" id="all_stats">
        <tbody>
            <tr data-row="0">
                <td class="right " data-stat="column1">1</td>
            </tr>
            <tr data-row="1">
                <td class="right " data-stat="column2">2</td>
            </tr>
        </tbody>
    </table>
</div>'''
        expected = ['<tr data-row="0">\n<td class="right " '
                    'data-stat="column1">1</td>\n</tr>',
                    '<tr data-row="1">\n<td class="right " '
                    'data-stat="column2">2</td>\n</tr>']
        div = 'table#all_stats'
        flexmock(utils) \
            .should_receive('_remove_html_comment_tags') \
            .and_return(html_string) \
            .once()

        result = utils._get_stats_table(MockHtml(html_string, expected), div)

        i = 0
        for element in result:
            i += 1

        assert i == 2
