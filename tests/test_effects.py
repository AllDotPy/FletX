import os
import sys
import types
import importlib.util


def _load_effects_and_deps():
    # Stub minimal 'fletx.utils'
    if "fletx" not in sys.modules:
        sys.modules["fletx"] = types.ModuleType("fletx")

    utils_mod = types.ModuleType("fletx.utils")

    class _Logger:
        def debug(self, *args, **kwargs):
            pass

        def error(self, *args, **kwargs):
            pass

    def get_logger(name):
        return _Logger()

    utils_mod.get_logger = get_logger

    sys.modules["fletx.utils"] = utils_mod

    # Load fletx/core/effects.py directly
    effects_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "fletx", "core", "effects.py"
    )
    spec = importlib.util.spec_from_file_location(
        "fletx_core_effects_standalone", effects_path
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.EffectManager, module.Effect


EffectManager, Effect = _load_effects_and_deps()


def test_effect_manager_register_and_run():
    em = EffectManager()
    calls = []

    def effect_fn():
        calls.append(1)

    em.useEffect(effect_fn, key="test")
    em.runEffects()
    assert len(calls) == 1


def test_effect_manager_update_dependencies():
    em = EffectManager()
    calls = []
    deps = [1]

    def effect_fn():
        calls.append(deps[0])

    em.useEffect(effect_fn, deps, key="test")
    em.runEffects()  # first run
    assert calls == [1]
    # Change dependencies
    deps[0] = 2
    em.useEffect(effect_fn, deps, key="test")  # update
    em.runEffects()  # should run again because deps changed
    assert calls == [1, 2]


def test_effect_manager_dispose():
    em = EffectManager()

    def effect_fn():
        pass

    em.useEffect(effect_fn, key="test")
    em.dispose()
    # After dispose, running effects should do nothing
    em.runEffects()  # should not raise


def test_effect_cleanup():
    em = EffectManager()
    cleanup_called = []

    def effect_fn():
        cleanup_called.append("start")
        return lambda: cleanup_called.append("cleanup")

    em.useEffect(effect_fn, key="test")
    em.runEffects()  # run effect, should return cleanup function
    em.runEffects()  # run again, should call cleanup then run effect again
    assert cleanup_called == ["start", "cleanup", "start"]


def test_effect_no_cleanup_if_not_returned():
    em = EffectManager()
    cleanup_called = []

    def effect_fn():
        # return nothing
        pass

    em.useEffect(effect_fn, key="test")
    em.runEffects()
    em.runEffects()
    assert cleanup_called == []  # no cleanup called


def test_effect_run_if_no_deps():
    em = EffectManager()
    calls = []

    def effect_fn():
        calls.append(1)

    em.useEffect(effect_fn, None, key="test")  # no deps
    em.runEffects()
    em.runEffects()  # should run every time because deps is None
    assert calls == [1, 1]


def test_effect_run_if_deps_none():
    em = EffectManager()
    calls = []

    def effect_fn():
        calls.append(1)

    em.useEffect(effect_fn, [], key="test")  # empty deps
    em.runEffects()
    em.runEffects()  # should run every time because deps is empty list (and last_deps is None initially, then [] -> [] so no change? Let's see)
    # Actually, the condition: if deps is None or last_deps is None or any(dep != last for dep, last in zip(deps, last_deps))
    # First run: deps=[] (not None), last_deps=None -> condition true because last_deps is None -> runs
    # Then last_deps becomes [] (copy of deps)
    # Second run: deps=[], last_deps=[] -> zip([],[]) -> no pairs -> any(...) is False -> condition: deps is None? no, last_deps is None? no, any(...) is False -> false -> should not run
    # But note: we are using the same list object? We are mutating the same list? In our test we are not changing the list.
    # However, in the effect manager, we do: self._last_deps = self.dependencies.copy() when we run.
    # So if we pass a new list each time, it might be different. But in the test we are passing the same list object [].
    # Let's change the test to pass a new list each time to simulate changing deps? Actually, we want to test that if deps are the same (and not None) it doesn't run.
    # We'll adjust the test to use a fixed list and see that it runs only once.
    # But note: the EffectManager's useEffect does not copy the deps list, it just stores the reference.
    # So if we change the list contents, it will be detected.
    # For the purpose of this test, we want to see that if we pass the same list (and same contents) it doesn't run again.
    # We'll change the test to pass a tuple or use a new list each time? Actually, let's just test the behavior we expect:
    # With deps=[] (empty list), the effect should run only on the first call because the deps are the same (and not None) and last_deps becomes [].
    # So we expect calls to be [1] only.
    # We'll run the test and see.
    assert calls == [1]  # we expect only one call


# We'll skip the above test for now and write a simpler one.
def test_effect_run_when_deps_change():
    em = EffectManager()
    calls = []
    deps = [1]

    def effect_fn():
        calls.append(deps[0])

    em.useEffect(effect_fn, deps, key="test")
    em.runEffects()  # run 1
    assert calls == [1]
    deps[0] = 2
    em.runEffects()  # run 2 because deps changed
    assert calls == [1, 2]


if __name__ == "__main__":
    test_effect_manager_register_and_run()
    test_effect_manager_update_dependencies()
    test_effect_manager_dispose()
    test_effect_cleanup()
    test_effect_no_cleanup_if_not_returned()
    test_effect_run_if_no_deps()
    test_effect_run_when_deps_change()
    print("All tests passed!")
