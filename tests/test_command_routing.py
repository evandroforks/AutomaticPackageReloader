import importlib.util
import os
import sys
import types
import unittest
from unittest.mock import patch


SOURCE = os.path.join(os.path.dirname(__file__), '..', 'package_reloader.py')


def load_command_module(versions):
    package = types.ModuleType('AutomaticPackageReloader')
    package.__path__ = []
    reloader = types.ModuleType('AutomaticPackageReloader.reloader')
    reloader.__path__ = []
    reloader.reload_package = lambda *args, **kwargs: None
    apr33 = types.ModuleType('AutomaticPackageReloader.reloader.apr33')
    apr33.ensure_helper = lambda directory: True
    apr33.cleanup_helper = lambda directory: True
    utils = types.ModuleType('AutomaticPackageReloader.utils')
    utils.ProgressBar = object
    utils.read_config = lambda *args: []
    utils.has_package = lambda name: True
    utils.package_of = lambda path: None
    utils.package_python_version = lambda name: versions[name]

    sublime = types.ModuleType('sublime')
    sublime_plugin = types.ModuleType('sublime_plugin')
    sublime_plugin.EventListener = object

    class WindowCommand:
        def __init__(self, window):
            self.window = window

        def name(self):
            if self.__class__.__name__ == 'PackageReloader33ReloadCommand':
                return 'package_reloader33_reload'
            return 'package_reloader_reload'

    sublime_plugin.WindowCommand = WindowCommand
    modules = {
        'AutomaticPackageReloader': package,
        'AutomaticPackageReloader.reloader': reloader,
        'AutomaticPackageReloader.reloader.apr33': apr33,
        'AutomaticPackageReloader.utils': utils,
        'sublime': sublime,
        'sublime_plugin': sublime_plugin,
    }
    with patch.dict(sys.modules, modules):
        spec = importlib.util.spec_from_file_location(
            'AutomaticPackageReloader.package_reloader', SOURCE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


class CommandRoutingTests(unittest.TestCase):
    def test_legacy_command_forwards_once_then_starts_reload(self):
        module = load_command_module({'Legacy': '3.3'})
        started = []
        dispatched = []

        class Window:
            def run_command(self, name, args):
                dispatched.append((name, args))
                if len(dispatched) > 1:
                    raise AssertionError('APR33 command forwarded recursively')
                bridge.run(**args)

        class Thread:
            def __init__(self, name, target, args):
                self.args = args

            def start(self):
                started.append(self.args)

        window = Window()
        bridge_class = type(
            'PackageReloader33ReloadCommand',
            (module.PackageReloaderReloadCommand,), {})
        bridge = bridge_class(window)
        command = module.PackageReloaderReloadCommand(window)

        with patch.object(module, 'Thread', Thread):
            command.run(package='Legacy')

        self.assertEqual(
            [('package_reloader33_reload', {'package': 'Legacy', 'extra_pkgs': []})],
            dispatched)
        self.assertEqual(1, len(started))
        self.assertEqual('Legacy', started[0][0])

    def test_modern_package_starts_reload_without_dispatch(self):
        module = load_command_module({'Modern': '3.8'})
        started = []

        class Window:
            def run_command(self, name, args):
                raise AssertionError('modern package was forwarded to APR33')

        class Thread:
            def __init__(self, name, target, args):
                self.args = args

            def start(self):
                started.append(self.args)

        with patch.object(module, 'Thread', Thread):
            module.PackageReloaderReloadCommand(Window()).run(package='Modern')

        self.assertEqual(1, len(started))
        self.assertEqual('Modern', started[0][0])


if __name__ == '__main__':
    unittest.main()
