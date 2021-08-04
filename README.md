# DGMQ Data Filter

DGMQ Data Filter is a script that allows DGMQ data owner to automatically filter data from .xlsx
format and output result into a .csv file in the present working directory. 

## Requirements
	- python=3.8*
	- pandas=1.2*
	- openpyxl=3.0*

## Installing
No installation required except prerequisite python modules. 

## Using DGMQT Data Filter
1) run the python script in the same directory containing:
	- exactly 2 .xlsx files
	- one of the .xlsx files is named "Records.xlsx"
2) the script will output result data into .csv file in present working directory


## Performed operations
	- Perform checks:
		Presence of 2 and only 2 .xlsx files
		Presence of file titled "Records.xlsx"
	- Load 2 .xlsx files in present working directory into python dataframe
	- Perform checks:
		Columns names match
		Columns data type match
	- Perform filtering:
		Remove when event ID is blank
		Remove when departure AND arrival dates are blank
		Remove when departure airport and Arrival airport are blank
		Keep data only if both are True:
			- LHJ column is either "DOH only" or within list of tracked counties
			- County column is either blank or within list of tracked counties
		Keep data only if both are True:
			- Departure date falls within 2 days before and 10 days after test date
			- Arrival date falls within 2 days before and 10 days after test date

## Contributors
Original author: Alexey Gilman
Date created:05/25/2021
