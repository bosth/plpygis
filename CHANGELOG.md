# Changelog

## [0.4.1] - DATE

### Changed

* Raise `WkbError` on malformed WKBs.

## [0.4.0] - 2024-04-22

### Added

* All the `Geometry` classes now have a `coordinates` property, and this is also used in the generation of GeoJSONs.
* The `Geometry` classes also now have a `__copy__()` method.
* Two new exceptions were added `CoordinateError` and `GeojsonError`.

### Chnaged

* plpygis has been migrated to use `pyproject.toml` instead of `setup.py`.
* The testing framework has been redone using `pytest`.

### Fixed

* Two unused parameters (`dimz` and `dimm`) were removed from `GeometryCollection`.

## [0.3.0] - 2024-04-08

### Fixed

* It was possible for invalid EWKBs to be generated for multigeometries with SRIDs. This fix does introduce a change to what `plpygis` accepts as valid parameters to any of the multigeometry types. However, it will only reject cases which would have produced bad EWKBs and anything that worked previously will still work now. This fixes https://github.com/bosth/plpygis/issues/10.

## [0.2.2] - 2024-03-08

### Changed

* plpygis now works with Shapely 2.x and drops support for 1.x.

### Fixed

* The license was updated to conform to the SPDX standard (https://github.com/bosth/plpygis/issues/9).

## [0.2.1] - 2023-03-11

### Changed

* The documentation was updated.

### Fixed

* `.pyc` files were being included in packages published to PyPI (https://github.com/bosth/plpygis/issues/8). [[vincentsarago](https://github.com/vincentsarago)]

## [0.2.0] - 2020-02-21

### Added

* plpygis now supports binary WKBs as described in (https://github.com/bosth/plpygis/issues/1). [[lovasoa](https://github.com/lovasoa)]

### Fixed

* A bug in handling little-endian WKBs was fixed (https://github.com/bosth/plpygis/issues/2). [[lovasoa](https://github.com/lovasoa)]

### Removed

* The dependency on nose for testing was removed.

## [0.1.0] - 2018-02-14
## [0.0.3] - 2018-01-21
## [0.0.2] - 2017-08-06
## [0.0.1] - 2017-07-30

[0.4.0]: https://github.com/bosth/plpygis/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/bosth/plpygis/compare/v0.2.2...v0.3.0
[0.2.2]: https://github.com/bosth/plpygis/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/bosth/plpygis/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/bosth/plpygis/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/bosth/plpygis/compare/v0.0.3...v0.1.0
[0.0.3]: https://github.com/bosth/plpygis/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/bosth/plpygis/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/bosth/plpygis/releases/tag/v0.0.1
