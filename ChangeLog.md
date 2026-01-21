# OldNews ChangeLog

## Unreleased

**Released: WiP**

- Fixed subscriptions not in folders not showing in navigation.
  ([#49](https://github.com/davep/oldnews/pull/49))
- Fixed remotely-removed subscriptions appearing back in navigation.
  ([#50](https://github.com/davep/oldnews/pull/50))
- Added the `AddSubscription` command for adding a new subscription feed.
  ([#53](https://github.com/davep/oldnews/pull/53))
- Fixed freshly-added subscriptions not having their article backlog
  downloaded. ([#55](https://github.com/davep/oldnews/pull/55))
- Fixed unread count missing unread articles not in folders.
  ([#56](https://github.com/davep/oldnews/pull/56))
- Added the `RenameSubscription` command for renaming the current
  subscription. ([#59](https://github.com/davep/oldnews/pull/59))

## v0.4.0

**Released: 2026-01-20**

- Tidy up the display and focus when the article list goes empty.
  ([#32](https://github.com/davep/oldnews/pull/32))
- Changed `OpenOrigin` into `OpenHomePage` and built it around the URL of
  the current subscription rather than the origin URL of the current
  article. ([#33](https://github.com/davep/oldnews/pull/33))
- Added the `CopyHomePageToClipboard` command for copying the current
  subscription's homepage URL to the clipboard.
  ([#43](https://github.com/davep/oldnews/pull/43))
- Added the `CopyFeedToClipboard` command for copying the current
  subscription's feed URL to the clipboard.
  ([#43](https://github.com/davep/oldnews/pull/43))
- Added the `CopyArticleToClipboard` command for copying the current
  article's URL to the clipboard.
  ([#43](https://github.com/davep/oldnews/pull/43))
- Added the `Copy` command for copying a URL to the clipboard depending on
  the current context. ([#43](https://github.com/davep/oldnews/pull/43))

## v0.3.0

**Released: 2026-01-19**

- Made small improvements to article list refreshing.
  ([#21](https://github.com/davep/oldnews/pull/21))
- Moved the sync code out into its own class.
  ([#22](https://github.com/davep/oldnews/pull/22))
- Made some cosmetic tweaks to the article view.
  ([#23](https://github.com/davep/oldnews/pull/23))
- Added a `reset` command line command that can be used to erase all local
  data (and optionally force a logout).
  ([#27](https://github.com/davep/oldnews/pull/27))
- Removed the `--licence` command line switch.
  ([#29](https://github.com/davep/oldnews/pull/29))
- Removed the `--bindings` command line switch.
  ([#29](https://github.com/davep/oldnews/pull/29))
- Removed the "?" parameter for the `--theme` command line switch.
  ([#29](https://github.com/davep/oldnews/pull/29))
- Added a `licence`/`license` command line command that is used to show the
  application's licence. ([#29](https://github.com/davep/oldnews/pull/29))
- Added `bindings` command line command that is used to list all bindable
  commands. ([#29](https://github.com/davep/oldnews/pull/29))
- Added a `themes` command that is used to list all themes available to the
  application. ([#29](https://github.com/davep/oldnews/pull/29))

## v0.2.0

**Released: 2026-01-17**

- Using `NextUnread` and `PreviousUnread` while inside the navigation panel
  now moves the highlight to the next folder or subscription that has unread
  articles. ([#15](https://github.com/davep/oldnews/pull/15))
- Added the `OpenOrigin` command, which opens the origin URL for the current
  article. ([#16](https://github.com/davep/oldnews/pull/16))
- Small cosmetic tweaks to the way an article is shown.
  ([#17](https://github.com/davep/oldnews/pull/17))
- Added automatic cleaning of locally-held old read articles.
  ([#18](https://github.com/davep/oldnews/pull/18))
- Cleaned up some of the database declaration code.
  ([#19](https://github.com/davep/oldnews/pull/19))

## v0.1.0

**Released: 2026-01-16**

- Added the `Next` command, which moves to the next article regardless of
  read status. ([#12](https://github.com/davep/oldnews/pull/12))
- Added the `Previous` command, which moves to the previous article
  regardless of read status.
  ([#12](https://github.com/davep/oldnews/pull/12))
- Added the `MarkAllRead` command, which marks all unread articles in the
  current category as read.
  ([#13](https://github.com/davep/oldnews/pull/13))

## v0.0.2

**Released: 2026-01-09**

- Initial public build.

## v0.0.1

**Released: 2025-10-21**

- Initial placeholder package to test that the name is available in PyPI.

[//]: # (ChangeLog.md ends here)
