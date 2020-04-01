# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## Current version [0.0.8] - 2020-04-01

### Changed

- Get_info function: Due the website is updated, I need to modify the function to make it works again
- Change the display images in Readme

## [0.0.7] - 2020-03-21

### Added

 - Functions to generate lineplots to show the number of infected of different provinces and cities

## [0.0.6] - 2020-03-14

### Changed

- Get_info function: Due the website is updated, I need to modify the function to make it works again
- Save_info function: Same reason

## [0.0.5] - 2020-03-14

### Added

- Aggregation functions to generate the info in a city-level and province-level
- Do the aggregation after getting the data from RIVM page

## [0.0.4] - 2020-03-13

### Added

- Function to get the csv info
- Preprocess the csv_str: discard the last column
- Function to process and save the data
- History data (2020-03-12) as the workflow was broken at that day

### Changed

- Workflow

## [0.0.3] - 2020-03-08

### Added

- Enrich the daily data with the Dutch municipalities information
  - Add a column 'Province' in the saved csv file
  - Add a row listing the sum of infected number
- Add the history data (2020-02-27 - 2020-03-05)

### Changed

- Changed all the saved csv files into new format

## [0.0.2] - 2020-03-07

### Added

- Github workflow to update the data automatically

## [0.0.1] - 2020-03-07

### Added

- Functions to obtain and save the data
- Dockerfile to run the scripts

### Changed

- Update the dependency packages
- Update Readme

## [0.0.0] - 2020-03-06

### Added

- Initialize the whole project
- PR template
- TODO list
- Changelog
