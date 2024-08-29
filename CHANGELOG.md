# Changelog

## [0.5.4] - 2024-08-29

### Changed

* `WktError` now correctly inherits from `PlpygisError`

### Added

* Allow overriding SRID when reading from a WKT/EWKT

## [0.5.3] - 2024-08-18

### Fixed

* Bug in WKTs when there is an integer ending in 0

## [0.5.2] - 2024-08-09

### Changed

* WKTs now have full precision rather than just 6 decimal places

### Fixed

* Bug in conversion to Shapely when there is an SRID

## [0.5.1] - 2024-08-01

### Fixed

* Invalid WKB in certain circumstances

## [0.5.0] - 2024-07-31

### Changed

* `wkb` now always returns a WKB and not a EWKB
* `__copy__()` now performs a shallow copy for multigeometries
* `geometries` is immutable (make changes to members using overloaded operators to ensure type checking)

### Added

* Overloaded `len` and `[]` for multigeometries
* Overloaded `+` and `+=` operators for geometries
* `pop()` for multigeometries
* `__deepcopy__()` for geometries
* `from_wkt()` to read Well-known Text
* `ewkb` to explicitly request an SRID
* `wkt` and `ewkt` properties to write Well-known Text

## [0.4.2] - 2024-07-21

### Fixed

* Documentation
* CI works with Numpy 2.x

## [0.4.1] - 2024-04-30

### Changed

* Raise `WkbError` on malformed WKBs.

### Added

* New exception: `CollectionError`.

## [0.4.0] - 2024-04-22

### Added

* All the `Geometry` classes now have a `coordinates` property, and this is also used in the generation of GeoJSONs.
* The `Geometry` classes also now have a `__copy__()` method.
* Two new exceptions were added `CoordinateError` and `GeojsonError`.

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

[0.5.4]: https://github.com/bosth/plpygis/compare/v0.5.3...v0.5.4
[0.5.3]: https://github.com/bosth/plpygis/compare/v0.5.2...v0.5.3
[0.5.2]: https://github.com/bosth/plpygis/compare/v0.5.1...v0.5.2
[0.5.1]: https://github.com/bosth/plpygis/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/bosth/plpygis/compare/v0.4.2...v0.5.0
[0.4.2]: https://github.com/bosth/plpygis/compare/v0.4.1...v0.4.2
[0.4.1]: https://github.com/bosth/plpygis/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/bosth/plpygis/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/bosth/plpygis/compare/v0.2.2...v0.3.0
[0.2.2]: https://github.com/bosth/plpygis/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/bosth/plpygis/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/bosth/plpygis/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/bosth/plpygis/compare/v0.0.3...v0.1.0
[0.0.3]: https://github.com/bosth/plpygis/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/bosth/plpygis/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/bosth/plpygis/releases/tag/v0.0.1
