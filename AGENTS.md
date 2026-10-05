# AGENTS.md

Guidance for agents working in this repository.

## Project

Django Blueprint (`django-blueprint`, import name `blueprint`) is an installable Django package — not a Django project. It provides common CMS building blocks (abstract base models, custom model fields, validators, managers) so a Django app can gain CMS-like functionality without adopting a full CMS. It ships no views, URLs, settings, or `manage.py`.

- Python 3.12+ (required).
- Target Django 5.x and 6.x. Dev environment uses Django 6.x; keep code compatible with 5.x LTS.
- Only runtime dependency: `jsonschema`. Do not add runtime dependencies without a strong reason — this is a base-layer library.
- Installed apps use this package via `INSTALLED_APPS = ["blueprint", ...]`; the `blueprint` app has no models of its own (only abstract models), so it needs no migrations. `blueprint.media_library` (app label `dbp_media_library`) does have models and migrations.

## Layout

```
blueprint/
├── models.py          # Abstract base models (UUIDModel, TimeStampedModel, EditorModel,
│                      # ManualOrderModel, SoftDeletableModel, ContentModel,
│                      # SoftDeletableContentModel, SingletonModel)
├── fields.py          # HTMLField, FlexField (JSON-Schema validated), URLPathField,
│                      # MultipleChoiceField, TagField
├── validators.py      # JSONSchemaValidator (deconstructible)
├── managers.py        # SingletonManager, SoftDeletableManager
└── media_library/     # Concrete app: Media, Folder, MediaField/ManyMediaField/CropField,
    │                  # app label `dbp_media_library`
    └── migrations/    # Concrete migrations, keep committed
```

- Translations live in `blueprint/locale/` (nl). All user-facing strings must use `gettext_lazy` (`_()`).
- Database tables use the `dbp_` prefix (`db_table = "dbp_media"`, `"dbp_folder"`); keep this convention for new concrete models.

## Commands

Managed with Poetry:

```bash
poetry install                 # set up dev environment
poetry run pytest              # run the test suite
poetry run black .             # format (black, default settings — enforced)
poetry run black --check .      # verify formatting
```

Migrations for `media_library` (and any future concrete app) are generated against a throwaway settings module:

```bash
poetry run django-admin makemigrations dbp_media_library
```

Never hand-edit existing migrations that have been released; add a new migration instead.

### Testing

The suite uses pytest + pytest-django (configured in `pyproject.toml` under `[tool.pytest.ini_options]`):

- `tests/settings.py` — minimal settings: in-memory SQLite, `contenttypes` + `auth` + the `blueprint` apps, throwaway `MEDIA_ROOT`.
- `tests/models.py` — concrete models exercising the abstract bases, registered under the `blueprint` app label (the app has no migrations, so Django sync-creates their tables). `tests/conftest.py` imports this module so the models register before the test database is built.

Conventions:

- Every bug fix comes with a regression test.
- Known-but-unfixed bugs are documented with `@pytest.mark.xfail` tests (each references its roadmap item in `ROADMAP.md`, kept local). When fixing one, flip the test to expect success.
- Test models use explicit `db_table` values prefixed `test_` to avoid collisions.

## Code conventions

- Formatting: black, default settings (line length 88). Run `poetry run black .` before committing.
- Commit messages: Conventional Commits (`feat:`, `fix:`, `chore:`, ...), as used in the history.
- Classic Django admin integration is low priority: Blueprint's intended editing frontend is Django Content Studio (separate project). Do not add `django.contrib.admin`-specific code without being asked.
- New abstract models: `abstract = True` in `Meta`, design for composition (see how `ContentModel` combines `UUIDModel`, `TimeStampedModel`, `EditorModel`).
- New JSON-backed fields: subclass `models.JSONField`, use `kwargs.setdefault(...)` for defaults so callers can override, `default=list` for array-shaped fields, and implement `deconstruct()` when adding constructor parameters (see `FlexField`) so migrations can serialize the field.
- Custom validators: mark them `@deconstructible` and implement `__eq__` so migration state hashing stays stable.
- Editor/audit fields go through the abstract bases (`EditorModel.edited_by` references `settings.AUTH_USER_MODEL`) — never hardcode a user model.
- Soft deletion: `SoftDeletableModel.delete()` defaults to soft; `objects` sees everything, `available_objects` filters removed items. Preserve this two-manager pattern.

## Public API care

This is a published library (PyPI). Anything exported from `blueprint.models`, `blueprint.fields`, `blueprint.validators`, `blueprint.managers`, and `blueprint.media_library.*` is public API:

- Avoid breaking changes to base models and fields; downstream projects inherit from them and generate their own migrations. Renames/removals need a major version and a CHANGELOG entry.
- Changing a base model or a field's serialized form (e.g. its `deconstruct()` output) forces new migrations on every downstream project — treat such changes as high-impact.
- Keep `CHANGELOG.md` updated for user-visible changes (it is currently a stub; turn it into a proper Keep-a-Changelog-style file when the next release is cut).

## Versioning and releases

The version string exists in two places and must be kept in sync:

1. `pyproject.toml` (`[project] version`)
2. `blueprint/__init__.py` (`__version__`, plus the `VERSION` synonym)

Release flow:

1. Update both version strings (beta/stable pre-releases use e.g. `1.0.0-beta.3`).
2. Update `CHANGELOG.md`.
3. Commit with a `chore:`/`fix:` conventional message.
4. Tag as `v<version>` (e.g. `v1.0.0-beta.3`).
5. Build with `poetry build`; artifacts land in `dist/` (committed in this repo).
