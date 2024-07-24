"""Functions to probe NERSC for usage"""

import tqdm
import subprocess
import datetime

def convert_string_to_float(s: str) -> float:
    """
    This function converts a string to a float.

    Parameters
    ----------
    s : str
        The string to be converted. It can optionally end with 'M' or 'K' to indicate millions or thousands, respectively.

    Returns
    -------
    float
        The converted float value. If the conversion fails, it prints the string and 'failed' and returns 0.0.
    """
    s = s.strip()  # Remove leading and trailing spaces
    try:
        if s[-1] == 'M':
            return float(s[:-1]) * 1e6
        elif s[-1] == 'K':
            return float(s[:-1]) * 1e3
        else:
            return float(s)
    except:
        # print(f'failed to read string={s}') # happens too much
        return 0.0
    

def get_account_usage(account_name: str, start_year: int = 2021) -> dict:
    """
    This function retrieves the account usage data for a given account name from a start year to the current date.
    The values are returned on a per-day basis.

    Parameters
    ----------
    account_name: str
        The name of the account for which usage data is to be retrieved.
    start_year: int, optional
        The year from which to start retrieving usage data. Defaults to 2021.

    Returns
    -------
    dict 
        A dictionary containing the usage data for each date, starting from the specified start year.
        The keys are the dates in the format "YYYY-MM-DD", and the values are the total consumed energy for that 
        day. If there is an error running the sacct command, the value for that day is set to 0.0.
    """
    values = {}
    current_date = datetime.date(start_year, 1, 1)
    end_date = datetime.date.today()
    n_days = n_days = (end_date - current_date).days + 1

    with tqdm.tqdm(total = n_days) as pbar:
 
        while current_date <= end_date:
            start_date_str = current_date.strftime("%Y-%m-%d")
            end_date_str = (current_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            command = ["sacct",
                    f"--starttime={start_date_str}", 
                    f"--endtime={end_date_str}", 
                    f"--account={account_name}",
                    "--format=ConsumedEnergy"]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode == 0:
                day_info = result.stdout.split('\n')[2:]
                if len(day_info) > 1:
                    day_total = [convert_string_to_float(r) for r in day_info if len(r) > 0]
                else:
                    day_total = [0.0]
                values[start_date_str] = sum(day_total)
            else:
                print("Error running sreport:", result.stderr)
                values[start_date_str] = 0.0

            pbar.update(1)

    return values


def get_user_usage(user: str, start_year: int = 2021) -> dict:
    """
    This function retrieves the account usage data for a given user name from a start year to the current date.
    The values are returned on a per-day basis.

    Parameters
    ----------
    user: str
        The name of the user for which usage data is to be retrieved.
    start_year: int, optional
        The year from which to start retrieving usage data. Defaults to 2021.

    Returns
    -------
    dict 
        A dictionary containing the usage data for each date, starting from the specified start year.
        The keys are the dates in the format "YYYY-MM-DD", and the values are the total consumed energy for that 
        day. If there is an error running the sacct command, the value for that day is set to 0.0.
    """
    values = {}
    current_date = datetime.date(start_year, 1, 1)
    end_date = datetime.date.today()
    n_days = n_days = (end_date - current_date).days + 1

    with tqdm.tqdm(total = n_days) as pbar:
 
        while current_date <= end_date:
            start_date_str = current_date.strftime("%Y-%m-%d")
            end_date_str = (current_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            command = ["sacct",
                    f"--starttime={start_date_str}", 
                    f"--endtime={end_date_str}", 
                    f"--user={user}",
                    "--format=ConsumedEnergy"]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode == 0:
                day_info = result.stdout.split('\n')[2:]
                if len(day_info) > 1:
                    day_total = [convert_string_to_float(r) for r in day_info if len(r) > 0]
                else:
                    day_total = [0.0]
                values[start_date_str] = sum(day_total)
            else:
                print("Error running sreport:", result.stderr)
                values[start_date_str] = 0.0

            pbar.update(1)

    return values