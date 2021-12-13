import datetime
import numpy as np
from command_handler import pretty_delta, shorten_name


def test_pretty_delta():
    # january 1 2021 at midnight
    now = datetime.datetime(2021, 1, 1)

    diff = datetime.timedelta(seconds=640.991709)
    assert pretty_delta(now - diff, now) == "10 minutes 40 seconds ago"
    diff = datetime.timedelta(seconds=9139.466984)
    assert pretty_delta(now - diff, now) == "2 hours 32 minutes ago"
    diff = datetime.timedelta(seconds=1517.317412)
    assert pretty_delta(now - diff, now) == "25 minutes 17 seconds ago"
    diff = datetime.timedelta(seconds=601.990568)
    assert pretty_delta(now - diff, now) == "10 minutes 1 second ago"
    diff = datetime.timedelta(seconds=86.833506)
    assert pretty_delta(now - diff, now) == "1 minute 26 seconds ago"
    diff = datetime.timedelta(seconds=3021.714242)
    assert pretty_delta(now - diff, now) == "50 minutes 21 seconds ago"
    diff = datetime.timedelta(seconds=108.475011)
    assert pretty_delta(now - diff, now) == "1 minute 48 seconds ago"
    diff = datetime.timedelta(seconds=153389.515296)
    assert pretty_delta(now - diff, now) == "1 day 18 hours ago"
    diff = datetime.timedelta(seconds=483570.702954)
    assert pretty_delta(now - diff, now) == "5 days 14 hours ago"
    diff = datetime.timedelta(seconds=45.682237)
    assert pretty_delta(now - diff, now) == "45.7 seconds ago"
    diff = datetime.timedelta(seconds=4.568223)
    assert pretty_delta(now - diff, now) == "4.57 seconds ago"

    date = datetime.datetime(2021, 1, 1)
    now = datetime.datetime(2021, 1, 3)
    assert pretty_delta(date, now) == "2 days 0 hours ago"

    date = datetime.datetime(2021, 1, 1)
    now = datetime.datetime(2021, 10, 1)
    assert pretty_delta(date, now) == "on January 1, 2021"

    date = datetime.datetime(2021, 1, 1)
    now = datetime.datetime(2021, 2, 1)
    assert pretty_delta(date, now) == "on January 1"
    assert pretty_delta(now, date) == "in the future?"

def test_shorten_name():
    assert shorten_name("abc") == "abc"
    test_str = "0123456789"
    assert shorten_name(test_str, 6) == "012..."
    assert shorten_name(test_str, 9) == "012345..."
    assert shorten_name(test_str, 10) == "0123456789"
