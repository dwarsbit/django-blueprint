# Changelog

## Unreleased

Release-candidate fixes found in the pre-1.0.0 review.

- 👾 Packages now ship the compiled `nl` translation catalog: the `.mo` file was excluded from builds by a `.gitignore` rule and pip installs silently had no translations
- 🎁 `FlexField` and `MultipleChoiceField` keep their built-in validation when caller-supplied `validators` are passed — custom validators are appended instead of silently replacing the schema/options validation
- 👾 `URLPathField` no longer crashes on `None` values (with `null=True`) and keeps the root path `/` intact instead of turning it into an empty string
- 👾 `Media.__str__` no longer crashes for instances without a file; it falls back to the name or primary key
- 🧹 `TagField` and `HashTagField` pass non-list JSON values through unchanged instead of iterating them
- 🧹 `HTMLField` only sanitizes string values
- 🧹 The `URLPathField` validator messages and the media library app's verbose name are now translatable; the `nl` catalog ships their translations

## v1.0.0-rc.1

The stabilization and API refinement pass ahead of 1.0.0. Items marked ⚠️ are
breaking for pre-1.0 users and may require running `makemigrations` in
downstream projects.

- 🧩 `SingletonModel` now enforces a single row at the database level via a unique `singleton` column — ⚠️ downstream projects must run `makemigrations`
- 🧩 `QuerySet.delete()` on soft-deletable models now soft-deletes (stamps `removed_at`) instead of removing rows; note that cascade deletes driven by Django's collector still hard-delete
- 🎁 `MultipleChoiceField` validates values against its `options` via the new `ChoiceOptionsValidator`
- 🎁 `MediaField`/`ManyMediaField` default `to` to the `Media` model, so `MediaField(file_type="image")` works without a keyword-only `to`
- ⚠️ `Media.size` stores the exact size in bytes (`PositiveBigIntegerField`) instead of rounded kilobytes — schema change, run `makemigrations`
- 🎁 New `HashTagField` for hashtags: values are normalized on save to lowercase, without any whitespace or `#` signs, deduplicated
- 🎁 `HTMLField` sanitizes HTML on save with a safe built-in allowlist sanitizer (powered by nh3, now a required dependency); customize it per field via `HTMLField(sanitizer=...)` or project-wide via the new `BLUEPRINT["HTML_SANITIZER"]` setting
- ⚠️ `HTMLField` no longer stores raw HTML by default — sanitize outside the model, or point the sanitizer at a passthrough, if you relied on raw storage
- ⚠️ `TagField` is opinion-free: on save it trims surrounding whitespace and drops duplicates and empty results — it no longer lowercases or strips `#`
- ⚠️ `SoftDeletableModel.delete()` matches Django's signature and returns a `(count, {model: count})` tuple for soft deletes instead of `None`
- ⚠️ `MultipleChoiceField` now serializes its `options`, and `URLPathField` keeps its built-in path validators when custom ones are passed — both change the fields' `deconstruct()` output, generating a field alteration in downstream projects
- 👾 Fixes `ManualOrderModel.reorder()` crashing: it accessed the manager through the instance
- 👾 Fixes `SingletonManager.create()` raising `TypeError` when the singleton already exists; it now updates the existing instance
- 👾 Fixes `Media.save()` crashing when the instance has no file
- 👾 Fixes the `alt_text` verbose name msgid ("Alt text"); the Dutch translation "Alt-tekst" now activates through the `nl` catalog
- 🧪 Adds a pytest + pytest-django test suite and a CI matrix (Python 3.12/3.13 × Django 5.2/6.0, plus a formatting check)
- 📚 Adds the Docusaurus documentation site, hosted on GitHub Pages at dwarsbit.github.io/django-blueprint

## v1.0.0-beta.2

- 👾 Adds migrations to the media library app (they were missing from the release)

## v1.0.0-beta.1

Initial pre-release! 🎉

- 🎁 Core abstract models: `UUIDModel`, `TimeStampedModel`, `EditorModel`, `ManualOrderModel`, `SoftDeletableModel`, `ContentModel`, `SoftDeletableContentModel`, `SingletonModel`
- 🎁 Custom fields: `HTMLField`, `FlexField`, `URLPathField`, `MultipleChoiceField`, `TagField`
- 🎁 Media library app with `Media`/`Folder` models and `MediaField`/`ManyMediaField`/`CropField`
- 🎁 Managers and validators: `SingletonManager`, `SoftDeletableManager`, `JSONSchemaValidator`
