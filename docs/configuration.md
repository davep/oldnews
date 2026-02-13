# Introduction

The way that OldNews works can be configured using a configuration file.
This section will describe what can be configured and how.

!!! note

    At the moment some configuration can be done via OldNews' UI; other things
    require that you edit the configuration file using your preferred text
    editor. This section documents those things that can only be configured
    via editing the configuration file.

The location of the configuration file will depend on how your operating
system and its settings; but by default it is looked for in
[`$XDG_CONFIG_HOME`](https://specifications.freedesktop.org/basedir-spec/latest/),
in an `oldnews` subdirectory. Mostly this will translate to the file being
called `~/.config/oldnews/configuration.json`.

## Keyboard bindings

OldNews allows for a degree of configuration of its keyboard bindings;
providing a method for setting up replacement bindings for the commands that
appear in the [command palette](using.md).

### Bindable commands

The following commands can have their keyboard bindings set:

```bash exec="on"
oldnews bindings | sed -e 's/^\([A-Z].*\) - \(.*\)$/- `\1` - *\2*/' -e 's/^    \(Default:\) \(.*\)$/    - *\1* `\2`/'
```

### Changing a binding

If you wish to change the binding for a command, edit the configuration file
and add the binding to the `bindings` value. For example, if you wanted to
change the binding used to mark an article as read, changing it from
<kbd>r</kbd> to <kbd>F6</kbd>, and you also wanted to use
<kbd>Shift</kbd>+<kbd>F6</kbd> to mark all articles as read, you would set
`bindings` to this:

```json
"bindings": {
    "MarkRead": "f6",
    "MarkAllRead": "shift+f6"
}
```

The designations used for keys is based on the internal system used by
[Textual](https://textual.textualize.io); as such [its caveats about what
works where
apply](https://textual.textualize.io/FAQ/#why-do-some-key-combinations-never-make-it-to-my-app).
The main modifier keys to know are `shift`, `ctrl`, `alt`, `meta`, `super`
and `hyper`; letter keys are their own letters; shifted letter keys are
their upper-case versions; function keys are simply <kbd>f1</kbd>,
<kbd>f2</kbd>, etc; symbol keys (the likes of `#`, `@`, `*`, etc...)
generally use a name (`number_sign`, `at`, `asterisk`, etc...).

!!! tip

    If you want to test and discover all of the key names and combinations
    that will work, you may want to install
    [`textual-dev`](https://github.com/Textualize/textual-dev) and use the
    `textual keys` command.

    If you need help with keyboard bindings [please feel free to
    ask](index.md#questions-and-feedback).

## Local history size

OldNews keeps read articles for a period of file. By default this is 28
days. This can be changed in the configuration file.

```json
"local_history": 28,
```

## Startup refresh hold off period

OldNews will refresh with TheOldReader when you run it up. However, rather
than perform a refresh every time you run it up, it will skip the refresh if
you start it again within a certain period. By default this is 10 minutes.
This can be changed in the configuration file.

```json
"startup_refresh_holdoff_period": 600
```

[//]: # (configuration.md ends here)
