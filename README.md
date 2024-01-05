# authx-extra 💫

<p align="center">
<a href="https://authx.yezz.me" target="_blank">
    <img src="https://user-images.githubusercontent.com/52716203/136962014-280d82b0-0640-4ee5-9a11-b451b338f6d8.png" alt="AuthX">
</a>
<p align="center">
    <em>Extra utilities for authx, including session, profiler &amp; caching ✨</em>
</p>
<p align="center">
<a href="https://github.com/yezz123/authx-extra/actions/workflows/ci.yml" target="_blank">
    <img src="https://github.com/yezz123/authx-extra/actions/workflows/ci.yml/badge.svg" alt="ci">
</a>
<a href="https://pypi.org/project/authx-extra" target="_blank">
    <img src="https://img.shields.io/pypi/v/authx-extra?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://codecov.io/gh/yezz123/authx-extra">
    <img src="https://codecov.io/gh/yezz123/authx-extra/branch/main/graph/badge.svg"/>
</a>
</p>
</p>

---

**Source Code**: <https://github.com/yezz123/authx-extra>

**Documentation**: <https://authx.yezz.me/>

---

## Features 🔧

- [x] Using Redis as a session store & cache.
- [x] Support HTTPCache.
- [x] Support Sessions and Pre-built CRUD functions and Instance to launch Redis.
- [x] Support Middleware of [pyinstrument](https://pyinstrument.readthedocs.io/) to check your service performance.
- [x] Support Middleware for collecting and exposing [Prometheus](https://prometheus.io/) metrics.

## Development 🚧

### Setup environment 📦

You should create a virtual environment and activate it:

```bash
python -m venv venv/
```

```bash
source venv/bin/activate
```

And then install the development dependencies:

```bash
# Install dependencies
pip install -e .[test,lint]
```

### Run tests 🌝

You can run all the tests with:

```bash
bash scripts/docker.sh
```

### Format the code 🍂

Execute the following command to apply `pre-commit` formatting:

```bash
bash scripts/format.sh
```

## Links 🚧

- [Homepage](https://authx.yezz.me/)
- [FAQ](https://authx.yezz.me/faq/)
- [Release - AuthX](https://authx.yezz.me/release/)
- [MIT License](https://authx.yezz.me/license/)
- [Code of Conduct](https://authx.yezz.me/code_of_conduct/)
- [Help - Sponsors](https://authx.yezz.me/help/)

## License 📝

This project is licensed under the terms of the MIT License.
