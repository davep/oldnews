# OldNews - A TheOldReader client for the terminal

## Introduction

OldNews is a terminal-based client for
[TheOldReader](https://theoldreader.com). Right now it is an evolving work
in progress, built on top of [`oldas`](https://github.com/davep/oldas).

## Installing

### pipx

The application can be installed using [`pipx`](https://pypa.github.io/pipx/):

```sh
$ pipx install oldnews
```

### uv

The package can be install using [`uv`](https://docs.astral.sh/uv/getting-started/installation/):

```sh
uv tool install oldnews
```

## File locations

OldNews stores files in a `oldnews` directory within both [`$XDG_DATA_HOME` and
`$XDG_CONFIG_HOME`](https://specifications.freedesktop.org/basedir-spec/latest/).
If you wish to fully remove anything to do with OldNews you will need to
remove those directories too.

Expanding for the common locations, the files normally created are:

- `~/.config/oldnews/configuration.json` -- The configuration file.
- `~/.local/share/oldnews/*` -- The locally-held data.

## Getting help

If you need help, or have any ideas, please feel free to [raise an
issue](https://github.com/davep/oldnews/issues) or [start a
discussion](https://github.com/davep/oldnews/discussions). However, please
keep in mind that at the moment the application is very much an ongoing work
in progress; expect lots of obvious functionality to be missing and "coming
soon"; perhaps also expect bugs.

## TODO

See [the TODO tag in
issues](https://github.com/davep/oldnews/issues?q=is%3Aissue+is%3Aopen+label%3ATODO)
to see what I'm planning.

[//]: # (README.md ends here)
