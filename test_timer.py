import datetime as dt

from timer import Timer


def test_pause(freezer):
    """Start the timer, pause the timer, check time."""
    t = Timer()
    assert not t.running
    assert not t.paused
    assert not t.started

    t.start()  # time = 0
    assert t.running
    assert not t.paused
    assert t.started

    freezer.tick(delta=dt.timedelta(seconds=10))  # time = 10

    assert t.get_current_elapsed_time() == 10
    assert t.get_total_elapsed_time() == 10
    assert t.get_current_paused_time() == 0
    assert t.get_total_paused_time() == 0

    freezer.tick(delta=dt.timedelta(seconds=5))  # time = 15
    t.stop()
    assert not t.paused
    assert not t.running
    assert not t.started

    assert t.get_current_elapsed_time() == 0
    assert t.get_total_elapsed_time() == 15

    freezer.tick(delta=dt.timedelta(seconds=8))  # time = 23

    assert t.get_current_paused_time() == 0
    assert t.get_total_paused_time() == 0

    t.start()
    assert t.running
    assert not t.paused

    freezer.tick(delta=dt.timedelta(seconds=2))  # time = 25
    assert t.get_current_elapsed_time() == 2
    assert t.get_current_paused_time() == 0
    assert t.get_total_elapsed_time() == 17
    assert t.get_total_paused_time() == 0

    freezer.tick(delta=dt.timedelta(seconds=7))  # time = 32
    t.pause()

    assert t.paused
    assert not t.running

    assert t.get_current_elapsed_time() == 9
    assert t.get_current_paused_time() == 0
    assert t.get_total_elapsed_time() == 33
    assert t.get_total_paused_time() == 0


def test_pause_current_clock_time(freezer):
    """The current clock time must ignore the pause time."""
    t = Timer()

    t.start()
    freezer.tick(delta=dt.timedelta(seconds=7))

    assert t.get_current_elapsed_time() == 7

    t.pause()

    freezer.tick(delta=dt.timedelta(seconds=3))

    assert t.get_current_elapsed_time() == 7

    t.stop()

    assert t.get_current_elapsed_time() == 0


def test_pause_elapsed_time(freezer):
    """"""
    t = Timer()

    t.start()
    freezer.tick(delta=dt.timedelta(seconds=5))
    assert t.get_current_elapsed_time() == 5

    t.pause()
    freezer.tick(delta=dt.timedelta(seconds=2))
    t.start()
    assert t.get_current_elapsed_time() == 5

    freezer.tick(delta=dt.timedelta(seconds=3))
    assert t.get_current_elapsed_time() == 8
