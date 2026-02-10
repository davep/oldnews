# OldNews - A terminal-based client for TheOldReader

![OldNews](https://raw.githubusercontent.com/davep/oldnews/refs/heads/main/.images/oldnews-social-banner.png)

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/davep/oldnews/style-and-lint.yaml)](https://github.com/davep/oldnews/actions)
[![GitHub commits since latest release](https://img.shields.io/github/commits-since/davep/oldnews/latest)](https://github.com/davep/oldnews/commits/main/)
[![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/davep/oldnews)](https://github.com/davep/oldnews/issues)
[![GitHub Release Date](https://img.shields.io/github/release-date/davep/oldnews)](https://github.com/davep/oldnews/releases)
[![PyPI - License](https://img.shields.io/pypi/l/oldnews)](https://github.com/davep/oldnews/blob/main/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/oldnews)](https://github.com/davep/oldnews/blob/main/pyproject.toml)
[![PyPI - Version](https://img.shields.io/pypi/v/oldnews)](https://pypi.org/project/oldnews/)

## Introduction

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

## Getting started

OldNews only works if you have an account on
[TheOldReader](https://theoldreader.com). When you first run up OldNews you
will get a login screen:

![OldNews login](https://raw.githubusercontent.com/davep/oldnews/refs/heads/main/.images/login.png)

Enter your TheOldReader login details to log in.

> [!IMPORTANT]
> OldNews doesn't store your user name or password locally. It passes the
> details to the API of TheOldReader and then gets and locally stores a
> token for working with the API.

Once logged in TheOldReader will start to download a history of articles
form your subscriptions. From then on it will synchronise the read/unread
status as you read articles, and will refresh with the server if you request
a refresh, or when you next start the application (within a set time limit).

![Reading an article with OldNews](https://raw.githubusercontent.com/davep/oldnews/refs/heads/main/.images/reading.png)

## Using OldNews

At the moment the best way to get to know OldNews is to read the helps
screen; once in the main application you can see this by pressing
<kbd>F1</kbd>.

![OldNews help](https://raw.githubusercontent.com/davep/oldnews/refs/heads/main/.images/help.png)

You can also discover commands and their keyboard shortcuts using the
command palette:

![OldNews command palette](https://raw.githubusercontent.com/davep/oldnews/refs/heads/main/.images/command-palette.png)

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
discussion](https://github.com/davep/oldnews/discussions). However, please
keep in mind that at the moment the application is very much an ongoing work
in progress; expect lots of obvious functionality to be missing and "coming
soon"; perhaps also expect bugs.

## TODO

See [the TODO tag in
issues](https://github.com/davep/oldnews/issues?q=is%3Aissue+is%3Aopen+label%3ATODO)
to see what I'm planning.

[//]: # (README.md ends here)
