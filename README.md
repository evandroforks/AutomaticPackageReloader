# Automatic Package Reloader

Sublime Text package developers may find themselves have to close and re-open
ST multiple times when developing a package since ST doesn't reload all the
submodules of a package when the files are edited. This tiny package helps in
reloading the package without the need of reopening ST. The reloading order
of the modules is in the exact same order as if they are loaded by Sublime
Text.


## Installation

### By Package Control

1. Download & Install **`Sublime Text 3`** (https://www.sublimetext.com/3)
1. Go to the menu **`Tools -> Install Package Control`**, then,
    wait few seconds until the installation finishes up
1. Now,
    Go to the menu **`Preferences -> Package Control`**
1. Type **`Add Channel`** on the opened quick panel and press <kbd>Enter</kbd>
1. Then,
    input the following address and press <kbd>Enter</kbd>
    ```
    https://raw.githubusercontent.com/evandrocoan/StudioChannel/master/channel.json
    ```
1. Go to the menu **`Tools -> Command Palette...
    (Ctrl+Shift+P)`**
1. Type **`Preferences:
    Package Control Settings – User`** on the opened quick panel and press <kbd>Enter</kbd>
1. Then,
    find the following setting on your **`Package Control.sublime-settings`** file:
    ```js
    "channels":
    [
        "https://packagecontrol.io/channel_v3.json",
        "https://raw.githubusercontent.com/evandrocoan/StudioChannel/master/channel.json",
    ],
    ```
1. And,
    change it to the following, i.e.,
    put the **`https://raw.githubusercontent...`** line as first:
    ```js
    "channels":
    [
        "https://raw.githubusercontent.com/evandrocoan/StudioChannel/master/channel.json",
        "https://packagecontrol.io/channel_v3.json",
    ],
    ```
    * The **`https://raw.githubusercontent...`** line must to be added before the **`https://packagecontrol.io...`** one, otherwise,
      you will not install this forked version of the package,
      but the original available on the Package Control default channel **`https://packagecontrol.io...`**
    > [!WARNING]
    > Placing this custom channel before the default channel changes Package Control's resolution globally. Packages from this channel with the same name will override versions from the default channel.
    >
    > You can review the channel contents here:
    > https://raw.githubusercontent.com/evandrocoan/StudioChannel/master/channel.json
1. Now,
    go to the menu **`Preferences -> Package Control`**
1. Type **`Install Package`** on the opened quick panel and press <kbd>Enter</kbd>
1. Then,
    search for **`AutomaticPackageReloader`** and press <kbd>Enter</kbd>

See also:

1. [ITE - Integrated Toolset Environment](https://github.com/evandrocoan/ITE)
1. [Package control docs](https://packagecontrol.io/docs/usage) for details.


### Usage

To reload the package in the current window, use `Automatic Package Reloader: Reload Current Project`.

To activate reload on saving a `*py` file, use `Automatic Package Reloader: Toggle Reload On Save`.
Package Reloader will guess the package name from the file path in order to reload the submodules
and to reload the package.

The console panel will be shown when reloading fails, this behavior can be modified by
the settings.

![](shot.png)

### Add `Reload Current Package` build

It is recommended to add the following in your `.sublime-project` file so that <kbd>c</kbd>+<kbd>b</kbd> would invoke the reload action.

```
    "build_systems":
    [
      {
        "name": "Reload Current Package",
        "target": "package_reloader_reload",
      }
    ]
```

### Additional modules

APR would try its best to guess the dependent modules of the package. Sometimes, it may fail to detect all the dependencies. In those cases, developers could specify extra modules to be reloaded in the `.package_reloader.json` file.

```js
{
  "dependencies" : ["<module1>", "<module2>"]
}
```

### Credits
This is derived from the [code](https://github.com/divmain/GitSavvy/blob/599ba3cdb539875568a96a53fafb033b01708a67/common/util/reload.py) of Eldar Abusalimov.
