import importlib
import importlib.abc
import importlib.util
import os
import sys
import types
import unittest
from unittest.mock import patch


PACKAGE_DIR = os.path.join(os.path.dirname(__file__), '..')
RELOADER_DIR = os.path.join(PACKAGE_DIR, 'reloader')
PROBE_NAME = 'apr_extra_module_probe_for_test'


class ProbeLoader(importlib.abc.Loader):
    def create_module(self, spec):
        return None

    def exec_module(self, module):
        module.reload_count = getattr(module, 'reload_count', 0) + 1


class ProbeFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == PROBE_NAME:
            return importlib.util.spec_from_loader(fullname, ProbeLoader())
        return None


class ExtraModulesTests(unittest.TestCase):
    def test_loaded_extra_module_reloads_and_missing_module_is_ignored(self):
        finder = ProbeFinder()
        sys.meta_path.insert(0, finder)
        try:
            probe = importlib.import_module(PROBE_NAME)
            self.assertEqual(1, probe.reload_count)

            package = types.ModuleType('AutomaticPackageReloader')
            package.__path__ = [PACKAGE_DIR]
            reloader_package = types.ModuleType('AutomaticPackageReloader.reloader')
            reloader_package.__path__ = [RELOADER_DIR]
            resolver = types.ModuleType('AutomaticPackageReloader.reloader.resolver')
            resolver.resolve_parents = lambda name: set()
            utils = types.ModuleType('AutomaticPackageReloader.utils')
            utils.__path__ = []
            utils_package = types.ModuleType('AutomaticPackageReloader.utils.package')
            utils_package.package_python_matched = lambda name: True
            modules = {
                'AutomaticPackageReloader': package,
                'AutomaticPackageReloader.reloader': reloader_package,
                'AutomaticPackageReloader.reloader.resolver': resolver,
                'AutomaticPackageReloader.utils': utils,
                'AutomaticPackageReloader.utils.package': utils_package,
                'sublime': types.ModuleType('sublime'),
                'sublime_plugin': types.ModuleType('sublime_plugin'),
            }
            with patch.dict(sys.modules, modules):
                reloader = importlib.import_module(
                    'AutomaticPackageReloader.reloader.reloader')
                with patch.object(reloader, 'get_package_modules', return_value=iter(())):
                    reloader.reload_package(
                        'SamplePackage',
                        extra_modules=[PROBE_NAME, 'apr_missing_module_for_test'],
                        dummy=False,
                        verbose=False)

            self.assertEqual(2, probe.reload_count)
            self.assertNotIn('apr_missing_module_for_test', sys.modules)
        finally:
            sys.modules.pop(PROBE_NAME, None)
            sys.meta_path.remove(finder)


if __name__ == '__main__':
    unittest.main()
