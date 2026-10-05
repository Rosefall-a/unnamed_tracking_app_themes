# Unnamed Tracking App themes

Official and example CSS themes for the native web and phone interface.
Themes use a small `.utt` ZIP package, separate from executable `.utp` plugins.
They have no worker, SDK permissions or automatic updates.

Build with `python tools/build_themes.py`. Every branch push and pull request
validates the sources and publishes an `unsigned-dist` workflow artifact.
Download that artifact, extract a `.utt`, then open **Administration → Themes**
in a host with the theme installer and upload it. Review the publisher and theme
description before installing. Administrators enable themes and choose an
optional server default; each user chooses their own appearance.

- **Forest** is an official green theme with distinct light and dark surfaces.
- **Purple Blocks** is an intentionally loud example. It squares off the sidebar,
  cards, controls, popovers and dialogs to demonstrate CSS changes across the UI.

See [the package format](PACKAGE_FORMAT.md) to create another theme. Changes to
CSS never require rebuilding the host. Downloaded packages can be shared and
installed manually; there is no update service or signing requirement in this
initial format.
