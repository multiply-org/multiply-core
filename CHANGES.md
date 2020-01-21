## Version 0.6

## New Features and Improvements
* Support more time formats
* Introduced forward model registration system
* Integrated new forward model registration system into observation building
* Added Data Types for S1_SLC, S2_L" and S3_OLCI
* Improved Error Handling
* Adapated observations classes to work with S2 data in different formats
* Added S2L2 File Ref Creator
* Introduced concept of Model Data Types
* Adapted GeoTiff Writer to write tiles
* Updated environment
* Introduced concept of Aux Data Provision
* Added soil moisture and soil roughness to default variables
* Added tile determination
* Allow that forward models may have different priors than output variables
* Files from the same date are aggregated to a single observation

### Fixes
* Extended S2 L1C Data to support updated format
* Fixed requirements
* Made Data Validation more robust
* Added check whether data for date is available


## Version 0.5

## New Features
* Added Variable Library
* Added Generic Variable Validators
* Added S2 L1C Data in .SAFE-format as data type

### Improvements
* Extended Documentation


## Version 0.4.2

### Improvements
* Extended documentation
* Updated dependencies for general multiply environment

## Version 0.4.1

### Improvements and new Features
* Added CAMS TIFF as new data type
* Added MCD15A2 as new data type
* Added Writer PlugIn
* Added GeoTiff Writer
* Extended Observation Interfaces


## Version 0.4

### Improvements and new Features
* Added reprojection functionality
* Moved FileRef from Data Access to here
* Added Observations Interface
* Added Observations realization for ac-corrected S2 observations
* Introduced validator interface
* Added validators for various datatypes required for S2 AC
* Introduced DataTypeConstants


## Version 0.3

Version for presentation

### Features
* Utility methods for Atribute Dictionaries and Reprojections
* Skeleton of Documentation