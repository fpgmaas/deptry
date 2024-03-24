from __future__ import annotations

REQUIREMENTS_TXT_DEPRECATION_MESSAGE = (
    "Warning: In an upcoming release, support for the `--requirements-txt` command-line "
    "option and the `requirements_txt` configuration parameter will be discontinued. "
    "Instead, use `--requirements-file` or `requirements_file` under the `[tool.deptry]` "
    "section in pyproject.toml."
)

REQUIREMENTS_TXT_DEV_DEPRECATION_MESSAGE = (
    "Warning: In an upcoming release, support for the `--requirements-txt-dev` command-line "
    "option and the `requirements_txt_dev` configuration parameter will be discontinued. "
    "Instead, use `--requirements-file-dev` or `requirements_txt_dev` under the `[tool.deptry]` "
    "section in pyproject.toml."
)
