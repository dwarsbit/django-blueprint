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

- Translations live in `blueprint/locale/` (de, en, es, fr, it, nl — en falls back to the msgids). All user-facing strings must use `gettext_lazy` (`_()`). The compiled `.mo` catalogs are **committed** — they must ship in the wheel — so after changing a `.po` file, run `cd blueprint && django-admin compilemessages` and commit the `.mo` together with the `.po`. New msgids need a translation in every locale directory before a release.
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

CI (`.github/workflows/ci.yml`) runs the suite on GitHub Actions for every push and pull request: Python 3.12/3.13 × Django 5.2/6.0, plus a `black --check` job. Keep new code passing on all matrix legs.

## Code conventions

- Formatting: black, default settings (line length 88). Run `poetry run black .` before committing.
- Commit messages: Conventional Commits (`feat:`, `fix:`, `chore:`, ...), as used in the history.
- Classic Django admin integration is low priority: Blueprint's intended editing frontend is Django Content Studio (separate project). Do not add `django.contrib.admin`-specific code without being asked.
- New abstract models: `abstract = True` in `Meta`, design for composition (see how `ContentModel` combines `UUIDModel`, `TimeStampedModel`, `EditorModel`).
- New JSON-backed fields: subclass `models.JSONField`, use `kwargs.setdefault(...)` for defaults so callers can override, `default=list` for array-shaped fields, and implement `deconstruct()` when adding constructor parameters (see `FlexField`) so migrations can serialize the field.
- Custom validators: mark them `@deconstructible` and implement `__eq__` so migration state hashing stays stable.
- Editor/audit fields go through the abstract bases (`EditorModel.edited_by` references `settings.AUTH_USER_MODEL`) — never hardcode a user model.
- Package-level settings live under the `BLUEPRINT` dict in the Django settings (e.g. `HTML_SANITIZER`), always resolved lazily so test overrides work.
- Soft deletion: `SoftDeletableModel.delete()` defaults to soft; `objects` sees everything, `available_objects` filters removed items. Preserve this two-manager pattern.

## Public API care

This is a published library (PyPI). Anything exported from `blueprint.models`, `blueprint.fields`, `blueprint.validators`, `blueprint.managers`, and `blueprint.media_library.*` is public API:

- Avoid breaking changes to base models and fields; downstream projects inherit from them and generate their own migrations. Renames/removals need a major version and a CHANGELOG entry.
- Changing a base model or a field's serialized form (e.g. its `deconstruct()` output) forces new migrations on every downstream project — treat such changes as high-impact.
- `CHANGELOG.md` follows the house style shared with django-headless: per-version bullet lists with emoji prefixes (🎁 feature, 👾 bugfix, 🧩 model/manager behavior, 📚 docs, 🧪 tests, ⚠️ breaking). Record every user-visible change in the `Unreleased` section.

## Documentation website

The Docusaurus site in `website/` deploys to GitHub Pages at https://dwarsbit.github.io/django-blueprint/ via `.github/workflows/website.yml` on pushes to `main` that touch `website/**`. Verify changes with `npm run build` and `npm run typecheck` inside `website/` before committing.

Site conventions:

- The landing page is a React page (`src/pages/index.tsx`); documentation serves under `/docs` with an autogenerated sidebar (control ordering with `sidebar_position` front matter and `_category_.json` files).
- The site shares its visual identity with the Django Headless and Django Content Studio docs sites: the same Django-green palette (#0c4b33 primary, #44b78b accent), Inter + Space Grotesk fonts (self-hosted via `@fontsource`, loaded in `src/theme/Root.tsx`), and the hero/feature-card component patterns in `src/css/custom.css` (`dbp-` prefixed). Keep the three sites in sync when the shared style changes.
- Content must match the shipped API — when changing public behavior in `blueprint/`, update the affected docs pages in the same commit.

## Versioning and releases

The version string exists in two places and must be kept in sync:

1. `pyproject.toml` (`[project] version`)
2. `blueprint/__init__.py` (`__version__`, plus the `VERSION` synonym)

Release flow:

1. Update both version strings (pre-releases use e.g. `1.0.0-rc.1`).
2. Update `CHANGELOG.md` (re-cut `Unreleased` into the version section).
3. Commit with a `chore:` conventional message.
4. Tag as `v<version>` (e.g. `v1.0.0-rc.1`) and push `main` with the tag.
5. Build with `poetry build`; artifacts land in `dist/` (git-ignored).
6. Publish to PyPI with `poetry publish`.
