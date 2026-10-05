# Django Blueprint

[![PyPI version](https://badge.fury.io/py/django-blueprint.svg)](https://badge.fury.io/py/django-blueprint)
[![Python versions](https://img.shields.io/pypi/pyversions/django-blueprint.svg)](https://pypi.org/project/django-blueprint/)
[![Django versions](https://img.shields.io/badge/django-5.2%2B-blue.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

With Django Blueprint you get the common models and fields every CMS project rebuilds — without buying into a full CMS. Abstract base models, schema-validated JSON fields and a media library, ready to inherit.

📖 **Read the full documentation at [dwarsbit.github.io/django-blueprint](https://dwarsbit.github.io/django-blueprint/)**

## ✨ Features

- **🧩 Composable base models**: UUID keys, timestamps, an editor reference, soft deletion, manual ordering and singletons — abstract bases you mix into your models with plain inheritance
- **📐 JSON with a schema**: `FlexField` validates stored content against a JSON Schema, so editor-configurable content stays structured
- **🖼️ Media library**: `Media` and `Folder` models plus `MediaField`/`ManyMediaField` with a `file_type` hint for editors
- **🧭 URL paths and tags**: a unique, normalized URL path field and a tag field that trims, lowercases and deduplicates
- **🤝 Plays nice**: a plain library — no views, no templates, no lock-in; integrates with [Django Content Studio](https://github.com/dwarsbit/django-content-studio)

## 🚀 Quick Start

Install the package:

```bash
pip install django-blueprint
```

Add `blueprint` to `INSTALLED_APPS` (plus the media library app if you want it):

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "blueprint",
    "blueprint.media_library",  # optional
]
```

Build a content model:

```python
# apps/blog/models.py
from django.db import models
from blueprint.models import ContentModel


class Article(ContentModel):
    title = models.CharField(max_length=200)
    body = models.TextField()

    def __str__(self):
        return self.title
```

That's it! 🎉 Your model now has a UUID primary key, timestamps, an `edited_by` audit reference — and the media library, soft deletion and singletons are one import away.

## 📚 Documentation

All usage and configuration is documented at [dwarsbit.github.io/django-blueprint](https://dwarsbit.github.io/django-blueprint/):

- [Introduction](https://dwarsbit.github.io/django-blueprint/docs/intro) — what Blueprint is (and is not)
- [Getting started](https://dwarsbit.github.io/django-blueprint/docs/getting-started) — requirements, setup and your first content model
- [Content models](https://dwarsbit.github.io/django-blueprint/docs/models/content-models) — all abstract bases and how they compose
- [Soft deletion](https://dwarsbit.github.io/django-blueprint/docs/models/soft-deletion) — soft deletes for instances and querysets, two managers
- [Manual ordering](https://dwarsbit.github.io/django-blueprint/docs/models/manual-ordering) — order keys and gapless renumbering
- [Singletons](https://dwarsbit.github.io/django-blueprint/docs/models/singleton) — settings-style models guaranteed single-row
- [FlexField](https://dwarsbit.github.io/django-blueprint/docs/fields/flex-field) — JSON content validated against a JSON Schema
- [URL path, HTML, choices and tags](https://dwarsbit.github.io/django-blueprint/docs/fields/url-path-field) — the remaining fields
- [Media library](https://dwarsbit.github.io/django-blueprint/docs/media-library) — `Media`/`Folder` and the media reference fields
- [Validators and managers](https://dwarsbit.github.io/django-blueprint/docs/validators-and-managers) — the building blocks, usable on their own

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Run the test suite (`poetry run pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/dwarsbit/django-blueprint.git
cd django-blueprint

# Install dependencies (Poetry creates the virtual environment)
poetry install

# Run tests
poetry run pytest
```

## 🐛 Issues & Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/dwarsbit/django-blueprint/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/dwarsbit/django-blueprint/discussions)
- 📧 **Email**: leon@dwarsbit.nl

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on the shoulders of [Django](https://www.djangoproject.com/)
- Inspired by the headless CMS and Jamstack movement
- Thanks to all contributors and the Django community

## 🔗 Links

- [Documentation](https://dwarsbit.github.io/django-blueprint/)
- [PyPI Package](https://pypi.org/project/django-blueprint/)
- [GitHub Repository](https://github.com/dwarsbit/django-blueprint)
- [Changelog](CHANGELOG.md)
