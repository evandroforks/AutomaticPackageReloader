import sublime_plugin
import sublime
import os
from .reloader import reload_package


def expand_folder(folder, project_file):
    if project_file:
        root = os.path.dirname(project_file)
        if not os.path.isabs(folder):
            folder = os.path.abspath(os.path.join(root, folder))
    return folder


class PackageReloaderListener(sublime_plugin.EventListener):

    def on_post_save(self, view):
        if view.is_scratch() or view.settings().get('is_widget'):
            return False
        package_reloader_settings = sublime.load_settings("package_reloader.sulime-settings")
        if package_reloader_settings.get("reload_on_save"):
            sublime.set_timeout_async(view.window().run_command("package_reloader_reload"))


class PackageReloaderToggleReloadOnSaveCommand(sublime_plugin.WindowCommand):

    def run(self):
        package_reloader_settings = sublime.load_settings("package_reloader.sulime-settings")
        reload_on_save = not package_reloader_settings.get("reload_on_save", False)
        package_reloader_settings.set("reload_on_save", reload_on_save)
        onoff = "on" if reload_on_save else "off"
        sublime.status_message("Package Reloader: Reload on Save is %s." % onoff)


class PackageReloaderReloadCommand(sublime_plugin.WindowCommand):

    def run(self, pkg_name=None):
        spp = os.path.realpath(sublime.packages_path())

        if not pkg_name:
            view = self.window.active_view()
            file_name = view.file_name()
            if file_name:
                file_name = os.path.realpath(file_name)
                if file_name and file_name.endswith(".py") and spp in file_name:
                    pkg_name = file_name.replace(spp, "").split(os.sep)[1]

        if not pkg_name:
            pd = self.window.project_data()
            if pd and "folders" in pd and pd["folders"]:
                folder = pd["folders"][0].get("path", "")
                path = expand_folder(folder, self.window.project_file_name())
                pkg_name = path.replace(spp, "").split(os.sep)[1]

        if pkg_name:
            sublime.set_timeout_async(lambda: reload_package(pkg_name))