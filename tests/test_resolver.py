import importlib.util
import os
import sys
import types
import unittest
from unittest.mock import patch


SOURCE = os.path.join(os.path.dirname(__file__), '..', 'reloader', 'resolver.py')


def load_resolver(manager):
    package_control = types.ModuleType('package_control')
    package_manager = types.ModuleType('package_control.package_manager')
    package_manager.PackageManager = lambda: manager
    with patch.dict(sys.modules, {
            'package_control': package_control,
            'package_control.package_manager': package_manager}):
        spec = importlib.util.spec_from_file_location('resolver_for_test', SOURCE)
        resolver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(resolver)
    return resolver


class ResolverTests(unittest.TestCase):
    def test_legacy_dependency_chain_reaches_parent_packages(self):
        relationships = {
            'coverage': [],
            'legacy-middle': ['coverage'],
            'Middle': ['legacy-middle'],
            'Top': ['Middle'],
        }
        manager = types.SimpleNamespace(
            list_packages=lambda: ['Middle', 'Top'],
            list_dependencies=lambda: ['coverage', 'legacy-middle'],
            get_dependencies=lambda name: relationships[name],
            get_libraries=lambda name: self.fail('legacy facade should be used'),
        )
        resolver = load_resolver(manager)
        self.assertEqual(
            {'legacy-middle', 'Middle', 'Top'},
            resolver.resolve_parents('coverage'))

    def test_modern_library_objects_reach_parent_packages(self):
        class Library:
            def __init__(self, name):
                self.name = name

        manager = types.SimpleNamespace(
            list_packages=lambda: ['Middle', 'Top'],
            get_libraries=lambda name: {
                'Middle': [Library('coverage')],
                'Top': [Library('Middle')],
            }[name],
        )
        resolver = load_resolver(manager)
        self.assertEqual({'Middle', 'Top'}, resolver.resolve_parents('coverage'))


if __name__ == '__main__':
    unittest.main()
