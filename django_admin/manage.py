#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "django_admin.settings"
    )

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django could not be imported. "
            "Make sure Django is installed in your virtual environment."
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()