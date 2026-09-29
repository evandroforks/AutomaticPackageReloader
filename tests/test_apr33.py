import importlib.util
import os
import tempfile
import unittest


SOURCE = os.path.join(os.path.dirname(__file__), '..', 'reloader', 'apr33.py')
LEGACY_FIXTURE = os.path.join(os.path.dirname(__file__), 'fixtures', 'legacy_reloader.py.txt')
spec = importlib.util.spec_from_file_location('apr33_for_test', SOURCE)
apr33 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(apr33)


class GeneratedHelperTests(unittest.TestCase):
    def test_migrates_legacy_helper_and_preserves_custom_config(self):
        with tempfile.TemporaryDirectory() as root:
            directory = os.path.join(root, 'AutomaticPackageReloader33')
            os.mkdir(directory)
            helper = os.path.join(directory, apr33.HELPER_NAME)
            config = os.path.join(directory, apr33.CONFIG_NAME)
            with open(LEGACY_FIXTURE, 'rb') as stream:
                legacy_helper = stream.read()
            with open(helper, 'wb') as stream:
                stream.write(legacy_helper.replace(b'\n', b'\r\n'))
            custom_config = b'{"dependencies": ["CustomPackage"]}'
            with open(config, 'wb') as stream:
                stream.write(custom_config)

            self.assertTrue(apr33.ensure_helper(directory))
            with open(helper, 'rb') as stream:
                updated_helper = stream.read()
            self.assertNotIn(b'PathFinder', updated_helper)
            self.assertIn(b'from AutomaticPackageReloader import package_reloader', updated_helper)
            self.assertIn(b'class PackageReloader33ReloadCommand', updated_helper)
            compile(updated_helper.decode('utf-8'), helper, 'exec')
            with open(config, 'rb') as stream:
                self.assertEqual(custom_config, stream.read())
            self.assertTrue(os.path.isfile(os.path.join(directory, apr33.HIDDEN_NAME)))
            self.assertFalse(apr33.cleanup_helper(directory))
            self.assertTrue(os.path.isfile(helper))

    def test_custom_helper_is_untouched_and_not_hidden(self):
        with tempfile.TemporaryDirectory() as root:
            directory = os.path.join(root, 'AutomaticPackageReloader33')
            os.mkdir(directory)
            helper = os.path.join(directory, apr33.HELPER_NAME)
            custom_helper = b'# custom bridge\n'
            with open(helper, 'wb') as stream:
                stream.write(custom_helper)

            self.assertFalse(apr33.ensure_helper(directory))
            self.assertFalse(apr33.cleanup_helper(directory))
            with open(helper, 'rb') as stream:
                self.assertEqual(custom_helper, stream.read())
            self.assertEqual([apr33.HELPER_NAME], os.listdir(directory))

    def test_owned_helper_is_removed_but_extra_files_are_preserved(self):
        with tempfile.TemporaryDirectory() as root:
            directory = os.path.join(root, 'AutomaticPackageReloader33')
            self.assertTrue(apr33.ensure_helper(directory))
            extra = os.path.join(directory, 'custom.txt')
            with open(extra, 'w') as stream:
                stream.write('keep')
            self.assertFalse(apr33.cleanup_helper(directory))
            self.assertTrue(os.path.isfile(extra))
            os.unlink(extra)
            self.assertTrue(apr33.cleanup_helper(directory))
            self.assertFalse(os.path.exists(directory))


if __name__ == '__main__':
    unittest.main()
