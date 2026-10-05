# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

The stabilization pass ahead of 1.0.0. Pre-1.0 releases may include breaking
changes; items marked **breaking** below require action when upgrading.

### Added

- Database-level single-row guarantee for `SingletonModel` via a new unique
  `singleton` column (**breaking**: downstream projects must run
  `makemigrations`).
- `SoftDeletableQuerySet`: `QuerySet.delete()` on soft-deletable models now
  soft-deletes (stamps `removed_at`) instead of removing rows. Note: cascade
  deletes driven by Django's collector still hard-delete.
- `ChoiceOptionsValidator` in `blueprint.validators`; used by
  `MultipleChoiceField` to reject values outside its `options`.
- CI workflow: test matrix Python 3.12/3.13 × Django 5.2/6.0 plus a
  `black --check` job.
- Test suite (pytest + pytest-django).

### Changed

- `Media.size` now stores the exact size in bytes as a
  `PositiveBigIntegerField` instead of rounded kilobytes (**breaking**:
  schema change; run `makemigrations`).
- `MultipleChoiceField` now serializes its `options` in `deconstruct()`
  (**breaking**: generates a field alteration on downstream projects).
- `TagField` normalizes values on save — trims whitespace, strips leading
  `#`, lowercases, drops empties and duplicates — and defaults
  `blank=True` (**breaking** for projects relying on the raw values).
- `URLPathField` path validators are class-level `default_validators`;
  caller-supplied validators are appended instead of replacing them
  (**breaking**: `deconstruct()` output changed).
- `MediaField`/`ManyMediaField` default `to` to the `Media` model, so
  `MediaField(file_type="image")` works without keyword-only `to`.
- `SoftDeletableModel.delete()` matches Django's signature and returns a
  `(count, {model: count})` tuple for soft deletes instead of `None`
  (**breaking** for code reading the old return value).

### Fixed

- `ManualOrderModel.reorder()` no longer crashes: it accessed the manager
  through the instance.
- `SingletonManager.create()` no longer raises `TypeError` when the
  singleton already exists; it updates the existing instance.
- `Media.save()` no longer crashes when the instance has no file.
- `Media.alt_text` verbose name msgid corrected to "Alt text" (Dutch
  translation "Alt-tekst" now activates through the `nl` catalog).
- `Media.full_clean()` passes on an instance with defaults: the `folder`
  FK is now `blank=True`.

## [1.0.0-beta.2] - 2026-02-19

### Fixed

- Media library app now ships its migrations.

## [1.0.0-beta.1] - 2026-02-06

### Added

- Core abstract models (`UUIDModel`, `TimeStampedModel`, `EditorModel`,
  `ManualOrderModel`, `SoftDeletableModel`, `ContentModel`,
  `SoftDeletableContentModel`, `SingletonModel`), managers and validators.
- Custom fields: `HTMLField`, `FlexField`, `URLPathField`,
  `MultipleChoiceField`, `TagField`.
- Media library app with `Media`/`Folder` models and
  `MediaField`/`ManyMediaField`/`CropField`.

[Unreleased]: https://github.com/dwarsbit/django-blueprint/compare/v1.0.0-beta.2...HEAD
[1.0.0-beta.2]: https://github.com/dwarsbit/django-blueprint/compare/v1.0.0-beta.1...v1.0.0-beta.2
[1.0.0-beta.1]: https://github.com/dwarsbit/django-blueprint/commits/v1.0.0-beta.1
