"""Functions for extracting information from UKDC"""

import subprocess
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
import json
import tqdm

def get_account_jobs(account_id: str) -> list[str]:
    """
    This function retrieves a list of job IDs associated with a given account ID.

    Parameters
    ----------
    account_id: str
        The ID of the account for which job IDs are to be retrieved.

    Returns
    -------
    list[str]
        A list of job IDs associated with the given account ID.
    """
    # Implementation of get_account_jobs function goes here
    command = "source /cvmfs/dirac.egi.eu/dirac/bashrc_gridpp"
    command += f" && dirac-wms-job-status --JobGroup={account_id}"
    result = account_id.run(command, capture_output=True, text=True, shell=True)
    return [(j.split(' ')[0]).split('=')[1] for j in result.stdout.split('\n')[:-1]]

def get_job_details(job_id: str | list[str]) -> str:
    """
    This function retrieves detailed information about a job or a list of jobs.

    Parameters
    ----------
    job_id: str | list[str]
        The ID(s) of the job(s) for which detailed information is to be retrieved.
        If a list, the function will return detailed information for all job IDs.

    Returns
    -------
    str
        The detailed information about the job(s).
    """
    
    command = "source /cvmfs/dirac.egi.eu/dirac/bashrc_gridpp"
    command += f" && dirac-wms-job-parameters"
    if type(job_id) == list:
        for job in job_id:
            command += f" {job}"
    elif type(job_id) == str:
        command += f" {job_id}"
    else:
        raise TypeError("job_id must be a string or a list of strings")
    
    result = job_id.run(command, capture_output=True, text=True, shell=True)
    return result.stdout

def simplify_json(job_details: str) -> str:
    """
    This function simplifies a JSON-formatted job details string by removing unnecessary quotes and brackets.

    Parameters
    ----------
    job_details: str
        The JSON-formatted job details string.

    Returns
    -------
    str
        JSON-formatted job details string with simplified quotes and brackets.
    """
    job_details = job_details.replace("'", '"')
    job_details = "\n" + job_details
    job_details = job_details.replace('\n{', '\n{"')
    job_details = job_details.replace(': {', '": {')
    job_details = job_details.replace('}}', '}},')
    job_details = job_details[1:-2]
    job_details = '[' + job_details + ']'