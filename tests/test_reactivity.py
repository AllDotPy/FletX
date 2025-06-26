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

# --- Computed ---
def test_computed_tracks_and_updates():
    rx1 = Reactive(2)
    rx2 = Reactive(3)
    comp = Computed(lambda: rx1.value + rx2.value)
    assert comp.value == 5
    rx1.value = 5
    assert comp.value == 8
    rx2.value = 10
    assert comp.value == 15

# --- RxInt ---
def test_rxint_increment_decrement():
    rx = RxInt(5)
    rx.increment()
    assert rx.value == 6
    rx.decrement(2)
    assert rx.value == 4

# --- RxStr ---
def test_rxstr_append_and_clear():
    rx = RxStr("hi")
    rx.append(" there")
    assert rx.value == "hi there"
    rx.clear()
    assert rx.value == ""

# --- RxBool ---
def test_rxbool_toggle():
    rx = RxBool(True)
    rx.toggle()
    assert rx.value is False
    rx.toggle()
    assert rx.value is True

# --- RxList ---
def test_rxlist_append_remove_clear():
    rx = RxList([1, 2])
    rx.append(3)
    assert rx.value == [1, 2, 3]
    rx.remove(2)
    assert rx.value == [1, 3]
    rx.clear()
    assert rx.value == []
    rx.append(5)
    assert rx[0] == 5
    rx[0] = 10
    assert rx[0] == 10
    assert len(rx) == 1

# --- RxDict ---
def test_rxdict_set_get_del_update_clear():
    rx = RxDict({"a": 1})
    rx["b"] = 2
    assert rx["b"] == 2
    del rx["a"]
    assert "a" not in rx.value
    assert rx.get("b") == 2
    rx.update({"c": 3})
    assert rx["c"] == 3
    rx.clear()
    assert rx.value == {} 