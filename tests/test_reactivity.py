import pytest
from fletx.core.state import (
    ReactiveDependencyTracker, Observer, Reactive, Computed,
    RxInt, RxStr, RxBool, RxList, RxDict
)

# --- ReactiveDependencyTracker ---
def test_dependency_tracker_tracks_dependencies():
    rx = Reactive(1)
    def computation():
        return rx.value + 1
    result, deps = ReactiveDependencyTracker.track(computation)
    assert result == 2
    assert rx in deps

# --- Observer ---
def test_observer_notifies_on_change():
    rx = Reactive(0)
    called = []
    def callback():
        called.append(True)
    obs = rx.listen(callback)
    rx.value = 1
    assert called
    obs.dispose()
    called.clear()
    rx.value = 2
    assert not called

def test_observer_auto_dispose():
    rx = Reactive(0)
    called = []
    def callback():
        called.append(True)
    obs = rx.listen(callback, auto_dispose=True)
    obs.dispose()
    rx.value = 1
    assert not called

# --- Reactive ---
def test_reactive_value_and_observers():
    rx = Reactive(10)
    assert rx.value == 10
    rx.value = 20
    assert rx.value == 20
    called = []
    rx.listen(lambda: called.append(rx.value))
    rx.value = 30
    assert called[-1] == 30

