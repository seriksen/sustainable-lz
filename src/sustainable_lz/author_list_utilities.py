import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import geopy.distance as dist
import airportsdata
from geopy.distance import great_circle
import requests
import matplotlib
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import io
import sys
from copy import deepcopy

class author_list_util:
    """
        This is just Josh wrapping up Sam E.'s code to use the author lsit
    """


    def __init__(self,attendance_list_df=None,authorship_list_df=None):
        """
            attendance_list_df: Attendence list is a pandas DataFrame containing ['FirstName','LastName']
        """
        self.attendance_list=attendance_list_df
        #parse given or set authorship list
        if authorship_list_df is None:
            spreadsheet_id = "1J-8ehKgEcpmssEZ_dGRIp5lRQCg6tDonYYG87Rv__4I"
            sheet_id = "951549455"
            sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={sheet_id}"

            df = pd.read_csv(sheet_url)

            cut_down_df = df.loc[4:].dropna(subset=["Unnamed: 2"])

            final_info = cut_down_df[["Unnamed: 88", "Unnamed: 43","Unnamed: 87" , "# considered (x-check)", "PRIMARY PAGE", "Unnamed: 3"]]

            final_info.columns = ["Title", "Initials","FirstName", "LastName", "University", "isAuthor"]
            self.authorship_list=final_info
        else:
            self.authorship_list=authorship_list_df

        #if there's an attendence list, apply to data frame
        if self.attendance_list is not None:
            self.authorship_list['Attended']=True
            for index, row in final_info.iterrows():
                self.authorship_list.loc[index,'Attended'] = self.if_attendent(row)
            print("Attendence was %.1f%%"%(100*len(np.where(self.authorship_list['Attended'])[0])/len(self.authorship_list)))
        #Allows us to modify and restore later
        self.backup_authorship_list=deepcopy(self.authorship_list)

        #get instituitions information
        spreadsheet_id = "1J-8ehKgEcpmssEZ_dGRIp5lRQCg6tDonYYG87Rv__4I"
        sheet_id = "1098381277"
        sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={sheet_id}"

        df = pd.read_csv(sheet_url)

        institutions = df[["SECONDARY PAGE", "Unnamed: 7"]]
        institutions.columns = ["University", "Address"]
        institutions = institutions.iloc[4:]
        institutions = institutions.dropna(subset=['Address'])
        institutions['Address'] = institutions['Address'].str.replace('GBR', 'UK')
        institutions['Universities_FullName'] = institutions['University'] + ', ' + institutions['Address']
        institutions['Short_Address'] = institutions['Address'].apply(lambda x: ', '.join(x.split(', ')[-2:]))
        institutions['Corrected_Name'] = institutions['University'].apply(lambda x: x.split(' (')[0])
        institutions['Start_Address'] = institutions['Address'].apply(lambda x: ', '.join(x.split(', ')[:2]))
        

        print("Finding Instituition locations")
        # Initialize the geocoder
        geolocator = Nominatim(user_agent="university_geocoder")
        # To avoid hitting the service rate limits
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        institutions['location'] = institutions['University'].apply(geocode)
        institutions.loc[institutions['location'].isna(), 'location'] = institutions[institutions['location'].isna()]['Corrected_Name'].apply(geocode)
        institutions.loc[institutions['location'].isna(), 'location'] = institutions[institutions['location'].isna()]['Short_Address'].apply(geocode)
        institutions.loc[institutions['location'].isna(), 'location'] = institutions[institutions['location'].isna()]['Address'].apply(geocode)
        institutions.loc[institutions['location'].isna(), 'location'] = institutions[institutions['location'].isna()]['Start_Address'].apply(geocode)
        institutions['longitude'] = institutions['location'].apply(self.get_longitude)
        institutions['latitude'] = institutions['location'].apply(self.get_latitude)
        institutions[['longitude', 'latitude']] = institutions.apply(lambda row: self.correct_none(row) if pd.isna(row['latitude']) else (row['longitude'], row['latitude']), axis=1, result_type='expand')
        print("Correcting funky beahvoiur for Maryland")
        institutions.loc[institutions['University']=='University of Maryland','latitude']=38.98582939 
        institutions.loc[institutions['University']=='University of Maryland','longitude']=-76.937329584
        self.institutions=institutions
        self.backup_institutions=deepcopy(institutions)

        
        author_universities = self.authorship_list['University'].unique()
        self.author_university_locations = self.institutions[self.institutions['University'].isin(author_universities)]
        author_counts = self.authorship_list['University'].value_counts()
        self.author_university_locations["author_count"] = self.institutions['University'].map(author_counts)
        self.backup_author_university_locations=deepcopy(self.author_university_locations)

    def __getitem__(self, key):
        return self.authorship_list[key]
    def if_attendent(self,row):
        if row['FirstName'] not in np.array(self.attendance_list['FirstName']):
            return False
        if row['LastName'] not in np.array(self.attendance_list['LastName']):
            return False
        return True
    
    @staticmethod
    def get_latitude(location):
        try:
            return location.latitude
        except AttributeError:
            return None
    @staticmethod        
    def get_longitude(location):
        try:
            return location.longitude
        except AttributeError:
            return None
    @staticmethod
    def correct_none(entry):
        long = None
        lat = None
        print(entry['Short_Address'])
        if 'Daejeon' in entry['Short_Address']:
            lat = 36.375394
            long = 127.384520
        elif '57754-1700' in entry['Short_Address']:
            lat = 44.345992
            long = -103.755154
        return long, lat
    def filter_to_authors(self):
        """
            Filter the data to authors and count up (Sam E.'s code)
        """
        self.authorship_list=self.authorship_list.loc[self.authorship_list['isAuthor'] == 'TRUE']
        author_universities = self.authorship_list['University'].unique()
        self.institutions = self.institutions[self.institutions['University'].isin(author_universities)]
        self.author_university_locations = self.institutions[self.institutions['University'].isin(author_universities)]
        author_counts = self.authorship_list['University'].value_counts()
        self.author_university_locations["author_count"] = self.institutions['University'].map(author_counts)

    def filter_to_attendees(self):
        """
            Filter the data to attendees and recalulate things, I don't know Sam E's code lol
        """
        self.authorship_list=self.authorship_list.loc[self.authorship_list['Attended']]
        author_universities = self.authorship_list['University'].unique()
        self.institutions = self.institutions[self.institutions['University'].isin(author_universities)]
        self.author_university_locations = self.institutions[self.institutions['University'].isin(author_universities)]
        author_counts = self.authorship_list['University'].value_counts()
        self.author_university_locations["author_count"] = self.institutions['University'].map(author_counts)



    def remove_filters(self):
        self.authorship_list=self.backup_authorship_list
        self.institutions = self.backup_institutions
        self.author_university_locations = self.backup_author_university_locations

    @staticmethod
    def get_country_or_state(location):
        split_loc = location.split(', ')
        if 'United States' in split_loc:
            try:
                a = int(split_loc[-2])
                binning_region = split_loc[-3]
            except:
                binning_region = split_loc[-2]
        else:
            binning_region = split_loc[-1]
            if 'Svizzera' in binning_region:
                binning_region = 'Switzerland'
        return binning_region
    
    def group_by_country_or_state(self):
        # Calculate number of authors at each university

        # Create binning based on either country or state
        self.author_university_locations['Binning1'] = self.author_university_locations['location'].apply(lambda loc: self.get_country_or_state(loc.address) if loc else None)

        # Group by 'Binning1' and sum the 'author_count', also removes None - so Korea
        return self.author_university_locations.groupby('Binning1').agg({
            'author_count': 'sum',
            'University': 'first', # To make the assumption that everyone flies from one airport in that BinningRegion
            'longitude': 'first',
            'latitude': 'first'
        }).reset_index()

