"""Line-score parsing shared by NBA and NCAA men's basketball."""

import re


def _period(label):
    label = label.strip().upper()
    if label.isdigit():
        return ('regulation', int(label))
    match = re.fullmatch(r'(?:OT(\d*)|(\d*)OT)', label)
    if match:
        return ('overtime', int(match[1] or match[2] or 1))
    return None


def parse_line_score(table, regulation_periods):
    """Return the existing score summary and a verified overtime count.

    Use data-stat attributes before presentation classes. Require two complete,
    matching period sequences before declaring a count, including zero.
    """
    summary = {'away': [], 'home': []}
    sequences = []
    totals = []
    for team, row in zip(summary, table('tbody tr').items()):
        cells = list(row('td[data-stat]').items())
        periods = [(cell, _period(cell.attr('data-stat'))) for cell in cells]
        periods = [(cell, period) for cell, period in periods if period]
        if periods:
            try:
                totals.append(int(row('td[data-stat="T"]').text()))
            except ValueError:
                totals.append(None)
            sequence = []
            for cell, period in periods:
                sequence.append(period)
                try:
                    summary[team].append(int(cell.text()))
                except ValueError:
                    summary[team].append(None)
            sequences.append(sequence)
        else:
            # Historical markup and public summary parsing tests use CSS
            # classes without data-stat attributes. Preserve those summaries.
            for cell in list(row('td.right, td.center').items())[:-1]:
                try:
                    summary[team].append(int(cell.text()))
                except ValueError:
                    summary[team].append(None)
    if len(sequences) != 2 or sequences[0] != sequences[1]:
        return summary, None
    sequence = sequences[0]
    overtime = len(sequence) - regulation_periods
    expected = ([('regulation', i + 1) for i in range(regulation_periods)] +
                [('overtime', i + 1) for i in range(max(0, overtime))])
    if sequence != expected or any(
            value is None for scores in summary.values() for value in scores):
        return summary, None
    if totals != [sum(scores) for scores in summary.values()]:
        return summary, None
    return summary, overtime
