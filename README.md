# Page Graph Test Suite

## Setup

1. Build the [Brave browser](https://github.com/brave/brave-browser) with Page Graph support.
1. Ensure Python 3.7 or above is installed.
1. Install the [Poetry](https://poetry.eustace.io/docs/) dependency manager, if you haven't
   already.
1. Run `poetry install` in the repository directory to initialize its dependencies.

## Running Tests

To run all tests:

```
poetry run python test_runner.py <path to Brave>
```

To run all tests, in non-headless mode:

```
poetry run python test_runner.py <path to Brave> --no-headless
```

To run only a specific test:

```
poetry run python test_runner.py <path to Brave> --filter static_page
```

To run only tests matching one of a set of
[glob-style](https://en.wikipedia.org/wiki/Glob_(programming)) filters:

```
poetry run python test_runner.py <path to Brave> --filter 'static_*' 'cross_dom_*'
```

## Adding Tests

1. Drop your HTML/JS/CSS file(s) in `tests/html/`.
1. Write a Python test script in `tests/scripts/`. See
   [`static_page.py`](tests/scripts/static_page.py) for a simple example.

## Code Formatting

Python code in this repository is auto-formatted with the
[Lavender](https://pypi.org/project/lavender/) code formatter.

After the [initial setup](#setup), you can auto-format all Python source files in the repository by
running:

```
poetry run lavender .
```

Please do so before submitting changes.

## License

Copyright (C) 2019 [Brave Software, Inc](https://brave.com/)

This program is free software: you can redistribute it and/or modify it under the terms of the
Mozilla Public License, version 2.0.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the Mozilla
Public License for more details.

You should have received a copy of the Mozilla Public License along with this program. If not, see
[https://www.mozilla.org/en-US/MPL/2.0/](https://www.mozilla.org/en-US/MPL/2.0/).

Helpful resources:

- [Mozilla's MPL-2.0 FAQ](https://www.mozilla.org/en-US/MPL/2.0/FAQ/)
- [MPL-2.0 on TLDRLegal](https://tldrlegal.com/license/mozilla-public-license-2.0-\(mpl-2\))

### Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in
this work by you shall be licensed as above, without any additional terms or conditions.
