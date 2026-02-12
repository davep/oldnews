# OldNews ChangeLog

## Unreleased

**Released: WiP**

- When a folder is renamed, its expanded/collapsed state is now retained.
  ([#162](https://github.com/davep/oldnews/pull/162))
- Changed the default binding for `MoveSubscription` to <kbd>m</kbd>.
  ([#163](https://github.com/davep/oldnews/pull/163))
- Added the ability to download and view the text from the full page of an
  article; useful for those feeds that are stingy with the summary content.
  ([#164](https://github.com/davep/oldnews/pull/164))

## v1.0.0

**Released: 2026-02-11**

- More changes to how, when and where an article is marked as read when it
  is displayed. ([#133](https://github.com/davep/oldnews/pull/133))
- The unread status of articles marked as unread elsewhere is now
  synchronised. ([#134](https://github.com/davep/oldnews/pull/134))
- Added the `MarkRead` command for marking a specific article as read.
  ([#135](https://github.com/davep/oldnews/pull/135))
- Added the `MarkUnread` command for marking a specific article as unread.
  ([#135](https://github.com/davep/oldnews/pull/135))
- Added the `UserInformation` command for showing all known information
  about the currently-logged-in user.
  (#136[](https://github.com/davep/oldnews/pull/136))
- Added a header to the article list to make it clear what's being viewed.
  ([#139](https://github.com/davep/oldnews/pull/139))
- Made various cosmetic changes to the UI.
  ([#139](https://github.com/davep/oldnews/pull/139))
- Added the `ToggleCompact` command for toggling between a compact and more
  relaxed UI. ([#139](https://github.com/davep/oldnews/pull/139) and
  [#149](https://github.com/davep/oldnews/pull/149))
- Fixed a crash caused by https://github.com/Textualize/textual/issues/6360
  ([#140](https://github.com/davep/oldnews/pull/140))
- Improved the dialog that gets the name of a folder when moving a
  subscription. ([#156](https://github.com/davep/oldnews/pull/156))
- Tidied up the captions of various dialog buttons.
  ([#157](https://github.com/davep/oldnews/pull/157))

## v0.10.0

**Released: 2026-02-08**

- The new subscription dialog now defaults the feed to any URL found in the
  clipboard. ([#119](https://github.com/davep/oldnews/pull/119))
- Various small cosmetic tweaks to how dates and counts are shown.
  ([#120](https://github.com/davep/oldnews/pull/120))
- Changed the default binding for a number of different commands.
  ([#121](https://github.com/davep/oldnews/pull/121))
- Changed the way that an article is marked as read once it is displayed.
  ([#127](https://github.com/davep/oldnews/pull/127))
- BREAKING CHANGE: Removed `mark_read_on_read_timeout` from the application
  configuration. ([#127](https://github.com/davep/oldnews/pull/127))

## v0.9.0

**Released: 2026-02-06**

- BREAKING CHANGE: Rewrite of the local database support, swapped to using
  Tortoise ORM. ([#107](https://github.com/davep/oldnews/pull/107))
- Article download batch size can now be changed via the config file.
  ([#113](https://github.com/davep/oldnews/pull/113))
- Article downloads are now saved in batches.
  ([#113](https://github.com/davep/oldnews/pull/113))

## v0.8.0

**Released: 2026-02-01**

- Added a busy dialog when we're waiting for TheOldReader to add a new
  subscription. ([#99](https://github.com/davep/oldnews/pull/99))

## v0.7.0

**Released: 2026-01-28**

- The content of the `Navigation` panel is now sorted in alphabetical order,
  within folder. ([#91](https://github.com/davep/oldnews/pull/91),
  [#92](https://github.com/davep/oldnews/pull/92),
  [#95](https://github.com/davep/oldnews/pull/95))

## v0.6.0

**Released: 2026-01-27**

- When a subscription is removed elsewhere, its locally-held articles are
  now removed. ([#80](https://github.com/davep/oldnews/pull/80))
- Added an application log, which logs to the application's data directory.
  ([#84](https://github.com/davep/oldnews/pull/84))
- Added a `directories` command line command that can be used to see which
  directories are being used by the application.
  ([#88](https://github.com/davep/oldnews/pull/88))
- Added the ability to expand all folders in the navigation panel.
  ([#89](https://github.com/davep/oldnews/pull/89))
- Added the ability to collapse all folders in the navigation panel.
  ([#89](https://github.com/davep/oldnews/pull/89))

## v0.5.0

**Released: 2026-01-25**

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
- Added the `Rename` command for renaming the current folder or
  subscription. ([#59](https://github.com/davep/oldnews/pull/59) followed by
  [#62](https://github.com/davep/oldnews/pull/62))
- Added the `Remove` command for removing the current folder or
  subscription. ([#66](https://github.com/davep/oldnews/pull/66))
- Added the `MoveSubscription` command for moving a subscription from one
  folder to another. ([#68](https://github.com/davep/oldnews/pull/68))
- Added the `Information` command for showing information about the current
  folder, subscription or article.
  ([#75](https://github.com/davep/oldnews/pull/75))

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
