import datetime as dt
from main import Timer


def test_pause(mocker):
    """Start the timer, pause the timer, check time."""
    m = mocker.patch("main._now")
    now = dt.datetime.now(dt.timezone.utc)
    m.side_effect = [
        now,
        now + dt.timedelta(seconds=10),
        now + dt.timedelta(seconds=15),
        now + dt.timedelta(seconds=20),
        now + dt.timedelta(seconds=30),
    ]

    t = Timer()
    t.start()  # t = 0
    t.pause()  # t = 10
    t.start()  # t = 15
    t.stop()   # t = 20

    assert t.get_elapsed_seconds() == 15
