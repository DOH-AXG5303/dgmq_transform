import pandas as pd
import os, re
import numpy as np
from datetime import datetime, timedelta


def scan_directory(path_input = None):
    """
    Query directory for all .xlsx files. Defaults to present working directory. 

    args:
        path_input = string, path to directory to be scanned. 
    return: list of .xlsx file names
    """
    if path_input is None:
        path = "./"
        
    path = path_input 
    files = []

    # iterate filenames in directory and append .xlsx to files list
    for fname in os.listdir(path):
        if re.search(r'.xlsx', fname):
            files.append(fname)
        else:
            pass
    return files
def check_xlsx_files(files):
    """
    verify rules in the input list of strings (file names):
        1)pwd contains exactly 2 .xlsx files
        2)one of the .xlsx files is named "Records.xlsx"

    args:
        files: list of strings
    return: bool
    """

    # rules for files: exactly 2 files, Records.xlxs is present
    rules = [len(files) == 2,
             "Records.xlsx" in files]

    # verify all rules to be True
    if all(rules):
        print(
            "Both conditions are met. Present directory contains 2 .xlsx files, and one of these files is named Records.xlsx")
        return all(rules)

    else:
        print("One or both conditions are not met. Make sure there are 2 .xlsx files in present directory ")
        print("and 1 of these files is named Records.xlsx")
        return all(rules)
def load_xlsx_files(files, condition):
    """
    verify that condition is True
    import all the .xlsx files in the files list argument

    args:
        files: list of string
        condition: bool
    return: dict of dataframes
    """
    path = "./"  # path to pwd
    df_dict = {}

    # import excel into dataframes if file condition has been met
    if condition:
        for i in files:
            if i == "Records.xlsx":  # laod instructions for Records.xlsx file
                df_dict["Records"] = pd.read_excel((path + i),
                                                   sheet_name="Master",
                                                   engine="openpyxl")
            else:
                df_dict["Travel"] = pd.read_excel((path + i), engine="openpyxl")

    else:
        print("FAILED TO MEET CONDITION: Excel files were not imported")

    return df_dict
def import_data():
    files = scan_directory()
    condition = check_xlsx_files(files)
    df_dict = load_xlsx_files(files, condition)

    return df_dict
def drop_blank(input_df):
    """
    Remove all rows where:
        Event ID is blank
        Departure Date AND Arrival Date are blank
        Departure City AND Arrival City are blank
    args:
        input_df: dataframe
    :return: dataframe
    """
    df = input_df.copy()

    # dropping specific NaN values
    df.dropna(subset=["WDRS Event ID (Person) (Person)"], inplace=True)  # Event ID is blank

    # departire AND arrival are blank
    df.dropna(subset=['Trip Departure Date', 'Trip Arrival Date'], how="all", inplace=True)

    # Departure AND arrival city are blank
    df.dropna(subset=['Trip Departure City/Airport', 'Trip Arrival City/Airport'], how="all", inplace=True)

    return df
def remove_old_travel(input_df):
    """
    Remove rows where Arrival Date AMD Departure Date are >14 days from now.
    args:
        input_df: dataframe
    :return: dataframe
    """

    df = input_df.copy()

    now = datetime.today()
    days14 = timedelta(days=14)

    condition_arrival = (now - df['Trip Arrival Date']) > days14
    condition_departure = (now - df['Trip Departure Date']) > days14

    df.drop(df[condition_arrival & condition_departure].index, inplace=True)

    return df
def remove_counties(input_df):
    """
    Select only data where:
        County column is blank or within list of reported counties
        AND
        LHJ is "DOH Only" or within list of reported counties
    args:
        input_df: dataframe
    :return: dataframe
    """
    df = input_df.copy()

    condition_1 = df["County (Person) (Person)"].isin(
        [np.nan, 'Clallam',
         'Clark', 'Island', 'King', 'Kitsap', 'NE Tri',
         'San Juan', 'Skagit', 'Skamania', 'Snohomish',
         'Spokane', 'Whatcom', "Yakima", "out of state resident (non-WA)"])

    condition_2 = df["LHJ (Person) (Person)"].isin(
        ["DOH Only", 
         'Clallam', 'Clark', 'Island', 'King', 'Kitsap', 'NE Tri',
         'San Juan', 'Skagit', 'Skamania', 'Snohomish',
         'Spokane', 'Whatcom', "Yakima"])

    df = df[condition_1 & condition_2].copy()

    return df
def infection_check(input_df):
    """
    Filters out all data except the rows where either departure or arrival date fall within the range:
    [2 days before test, 10 days after test]

    args:
        input_df: dataframe
    return: datafrmae
    """
    df = input_df.copy()
    
    days2 = timedelta(days=2)
    days10 = timedelta(days=10)

    #departure date falls within the range of [2 days before test, 10 days after test]
    condition_departure = (df["Date Tested WDRS (Person) (Person)"]-days2 <= df["Trip Departure Date"]) & (df["Trip Departure Date"] <= (df["Date Tested WDRS (Person) (Person)"]+days10))

    #arrival date falls within the range of [2 days before test, 10 days after test]
    condition_arrival = (df["Date Tested WDRS (Person) (Person)"]-days2 <= df["Trip Arrival Date"]) & (df["Trip Arrival Date"] <= (df["Date Tested WDRS (Person) (Person)"]+days10))


    df = df[condition_departure & condition_arrival].copy()

    return df


def remove_if_present_in_records(df_travel, df_records):
    """
    Compare travel dataframe against records dataframe. Remove any rows from df_travel, if present
    in df_records.

    args:
        df_travel: dataframe (travel data)
        df_records: dataframe (records that were already sent to CDC)
    return: dataframe
    """

    df_records = df_records.copy()
    df = df_travel.copy()

    # drop duplicate event IDs in Records data. Prep for logical comparison
    df_records.drop_duplicates(subset="WDRS Event ID (Person) (Person)", inplace=True)

    # prepare index of two dataframes, set identified (Event ID) columns as index
    travel_index = df.set_index(keys="WDRS Event ID (Person) (Person)").index
    records_index = df_records.set_index(keys="WDRS Event ID (Person) (Person)").index

    # mask index values, keep True only if NOT present in records dataframe event ID
    mask = ~travel_index.isin(records_index)

    # resulting rows where event ID is NOT present in Records.xlsx master file
    df = df.loc[mask].copy()

    return df

if (__name__ == "__main__"):

    dataframes_dict = import_data()

    travel_df = (dataframes_dict["Travel"]
                 .pipe(drop_blank)
                 .pipe(remove_old_travel)
                 .pipe(remove_counties))

    travel_df = travel_df.pipe(infection_check)
    travel_df = remove_if_present_in_records(travel_df, dataframes_dict["Records"])

    travel_df.to_csv("./Result.csv", index=False)