# Introduction

![OldNews](images/oldnews-social-banner.png)

OldNews is a terminal-based client for
[TheOldReader](https://theoldreader.com). It provides the ability to read
news feeds while using TheOldReader as the server for your RSS/atom
subscriptions.

OldNews is and generally always will be fairly opinionated about the "best"
way to make use of TheOldReader (AKA how I like to use it); but where
possible I want to keep it quite general so it will be useful to anyone.

## Installing

### pipx

The application can be installed using [`pipx`](https://pypa.github.io/pipx/):

```sh
$ pipx install oldnews
```

### uv

The application can be installed using [`uv`](https://docs.astral.sh/uv/getting-started/installation/):

```sh
uv tool install oldnews
```

If you don't have `uv` installed you can use [uvx.sh](https://uvx.sh) to
perform the installation. For GNU/Linux or macOS or similar:

```sh
curl -LsSf uvx.sh/oldnews/install.sh | sh
```

or on Windows:

```sh
powershell -ExecutionPolicy ByPass -c "irm https://uvx.sh/oldnews/install.ps1 | iex"
```

Once installed run the `oldnews` command.

## File locations

OldNews stores files in an `oldnews` directory within both [`$XDG_DATA_HOME`
and
`$XDG_CONFIG_HOME`](https://specifications.freedesktop.org/basedir-spec/latest/).
If you wish to fully remove anything to do with OldNews you will need to
remove those directories too.

Expanding for the common locations, the files normally created are:

- `~/.config/oldnews/configuration.json` -- The configuration file.
- `~/.local/share/oldnews/*` -- The locally-held data.

## Getting help

If you need help, or have any ideas, please feel free to [raise an
issue](https://github.com/davep/oldnews/issues) or [start a
discussion](https://github.com/davep/oldnews/discussions).

## TODO

See [the TODO tag in
issues](https://github.com/davep/oldnews/issues?q=is%3Aissue+is%3Aopen+label%3ATODO)
to see what I'm planning.

[//]: # (index.md ends here)
