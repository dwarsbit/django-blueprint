"""
Module-level sanitizers used to test HTMLField customization. They live in
their own module so dotted import paths can be resolved from settings.
"""


def passthrough_sanitizer(value):
    return value


def upper_sanitizer(value):
    return value.upper()
