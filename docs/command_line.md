# The Command Line

OldNews has a number of commands and options that can be passed on the
command line. To see what is available you can use the `--help` switch:

```sh
oldnews --help
```
```bash exec="on" result="text"
oldnews --help
```

## Commands

### `directories`

The `directories` command can be used to see which directories have been
created by and are being used by OldNews.

```sh
oldnews directories
```
```bash exec="on" result="text"
oldnews directories
```

This is useful if you want to remind yourself where OldNews stories its data
and configuration.

### `license`

The `license` command shows the licence details of OldNews.

```sh
oldnews licence
```
```bash exec="on" result="text"
oldnews licence
```

### `bindings`

The `bindings` command shows all the available commands and their default
bindings.

```sh
oldnews bindings
```
```bash exec="on" result="text"
oldnews bindings
```

### `themes`

The `themes` command shows all the available themes.

```sh
oldnews themes
```
```bash exec="on" result="text"
oldnews themes
```

### `reset`

The `reset` command can used to reset the local data held by OldNews. The
command has some switches that can change how it works.

```sh
oldnews reset --help
```
```bash exec="on" result="text"
oldnews reset --help
```

If run as `oldnews reset` you will be prompted with a `y/n` prompt to
confirm that you want to remove your local data. If you use the `--yes`
switch the reset will be performed without confirming with you first.

When the local data is reset, the locally-held login token *isn't* reset;
this means you can reset the data, run up OldNews again and your data will
be freshly synchronised without needing to login again.

If you want to clear the login information too use the `--logout` switch.

[//]: # (command_line.md ends here)
