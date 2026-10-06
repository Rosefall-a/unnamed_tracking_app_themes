# Theme package format 1

A `.utt` (Unnamed Tracking Theme) is a ZIP containing `manifest.json`, its CSS
stylesheet, optional `README.md` and optional images/fonts. Paths remain relative
to the package, including URLs in CSS. Packages never contain JavaScript, Python
or executable files. The host installs files separately from the plugin runtime.

```json
{
  "format_version": 1,
  "id": "example.purple-blocks",
  "name": "Purple Blocks",
  "version": "1.0.0",
  "publisher": "Rosefall-a",
  "description": "Square corners and a very purple interface.",
  "kind": "example",
  "stylesheet": "theme.css",
  "supports": ["light", "dark"]
}
```

Identifiers contain 1–128 lowercase letters, digits, dots, underscores or dashes
and start with a letter or digit. `native` and `server` are reserved. Versions
have three non-negative numeric parts. Name/publisher are 1–120 characters;
description is at most 1,000 characters. `kind` is `official` or `example` and
describes this repository's collection, rather than a cryptographic identity.
`supports` lists `light`, `dark` or both. The stylesheet is a relative `.css` path.

The host rejects absolute/parent paths, duplicate paths, symlinks, encrypted
files, executable types and oversized archives. The upload limit is 10 MiB;
unpacked files total at most 20 MiB, with at most 128 files and 1 MiB per CSS file.
Allowed file types are CSS, Markdown, text, PNG, JPEG, WebP, GIF, SVG, WOFF/WOFF2,
TTF and OTF. UTF-8 JSON/CSS and supported relative asset paths are required.

Use the host's `--ui-*` variables and `html[data-theme="light"]` /
`html[data-theme="dark"]` selectors. CSS can override complete native menus,
including the sidebar, rather than only token colors. Native plugin pages share
these variables and styles. Theme stylesheets load only for the selected theme;
incompatible embedded plugin frames keep their own isolation boundary.

Only administrators install, enable, remove or choose the server default. Users
choose `server`, `native` or an enabled package. Removing/disabling a server
default returns it to the native interface. Unavailable personal selections use
the server default while retaining the user's preference for later restoration.
