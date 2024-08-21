# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 16:34:40 2023

@author: snazrul
"""
import os
import paramiko
import mysql.connector
import pandas as pd
import fnmatch
import re
import stat
from datetime import datetime, timedelta
import sys




connection = mysql.connector.connect(host=os.environ['MYSQL_HOST'],
                                user=os.environ['MYSQL_USERNAME'],
                                password=os.environ['MYSQL_PASSWORD'],
                                database=os.environ['MYSQL_DATABASE'] 
                                )


# SFTP connection settings
sftp_host = os.environ['Z_FTP_HOST']
sftp_port = 22
sftp_username = os.environ['Z_FTP_USERNAME']
sftp_password = os.environ['Z_FTP_PASSWORD']

# Create an SSH transport
transport = paramiko.Transport((sftp_host, sftp_port))
transport.connect(username=sftp_username, password=sftp_password)

# Create an SFTP client
sftp = paramiko.SFTPClient.from_transport(transport)



#vars
current_date = datetime.now()

first_day = current_date.replace(day=1)

if current_date.month == 12:
    last_day = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
else:
    last_day = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)

print("First day of the current month:", first_day.date())
print("Last day of the current month:", last_day.date())

current_year = str(datetime.now().year)
current_month_name = current_date.strftime("%B")
current_month_number = current_date.month

#/recordings/Meritize Support/2023/8- August 2023
#/recordings/Meritize Support - IVA i18n
sftp_folder = "/recordings/Meritize Support - IVA i18n"
sftp_folder_2  ="/recordings/Meritize Support/{}/{}- {} {}".format(current_year,current_month_number,current_month_name,current_year)
#Z:\COLLECTIONS\Customer Services - PCS call recordings\2024\3-March 2024
current_folder = ("Z:/COLLECTIONS/Customer Services - PCS call recordings/{}").format(current_year)

current_sub_folder = ("{}/{}-{} {}").format(current_folder,current_month_number,current_month_name,current_year)

# Check if the folder exists
if not os.path.exists(current_folder):
    # Create the folder
    os.makedirs(current_folder)
    print(f"Folder '{current_folder}' created successfully.")
else:
    print(f"Folder '{current_folder}' already exists.")

#check if subfolder exists    
if not os.path.exists(current_sub_folder):
    # Create the folder
    os.makedirs(current_sub_folder)
    print(f"Folder '{current_sub_folder}' created successfully.")
else:
    print(f"Folder '{current_sub_folder}' already exists.")

date_to_use = []

if len(os.listdir(current_sub_folder)) == 0:
    print('True')
    date_to_use.append(first_day.date())
    
else:
    print('False')
    existing_files = list(os.listdir(current_sub_folder))
    last_date = (existing_files[-1])
    original_date = datetime.strptime(last_date, "%m_%d_%Y")
    one_day = timedelta(days=1)
    new_date = original_date + one_day
    formatted_date_str = new_date.strftime("%Y-%m-%d")
    date_to_use.append(formatted_date_str)
    print(formatted_date_str)


files = '''select
*
from table;

'''.format(date_to_use[0], last_day.date())



files_list = pd.read_sql(files, connection)

if len(files_list) == 0:
    print('No new files to copy')
    sftp.close()
    transport.close()
    sys.exit()
else:

    print('T')
    
    file_list_2 = files_list['call_id'].astype(str).tolist()
    glob_file_list = [item + "*.wav" for item in file_list_2]
    
    
    
    # List files in the remote folder that match the pattern
    all_files = sftp.listdir(sftp_folder)
    
    all_files_2 = sftp.listdir(sftp_folder_2)
    
    matching_files = [file for file in all_files if any(fnmatch.fnmatch(file, pattern) for pattern in glob_file_list)]
    
    matching_files_2 = [file for file in all_files_2 if any(fnmatch.fnmatch(file, pattern) for pattern in glob_file_list)]
    
    destination_folder = current_sub_folder
    
    # check folder 1 for files and copy 
    for filename in matching_files:
        if os.path.exists(f"{current_sub_folder}/{filename}"):
            print(f"The file '{filename}' exists in the folder.")
        else:
            sftp.get(f"{sftp_folder}/{filename}", f"{current_sub_folder}/{filename}")
            print(f"The file '{filename}' has been copied.")
            
            
    # check folder 2 for files and copy 
    for filename in matching_files_2:
        if os.path.exists(f"{current_sub_folder}/{filename}"):
            print(f"The file '{filename}' exists in the folder.")
        else:
            sftp.get(f"{sftp_folder_2}/{filename}", f"{current_sub_folder}/{filename}")
            print(f"The file '{filename}' has been copied.")
        
        
    os.listdir(current_sub_folder)
    
    
    
    #---------------------------------------------------------------------------------------------------------
    
    remote_path = ""
    # 
    
    # Create an SFTP client and connect
    transport = paramiko.Transport((sftp_host, sftp_port))
    transport.connect(username=sftp_username, password=sftp_password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    
    # List all files in the remote folder
    # List all files in the remote folder
    files = sftp.listdir( remote_path)
    
    # Iterate through each file
    for file_name in files:
        # Check if the item is a file (not a directory)
        try:
            file_attr = sftp.stat(os.path.join(remote_path, file_name))
            if not stat.S_ISREG(file_attr.st_mode):
                continue  # Skip directories
        except Exception as e:
            print(f"Error checking '{file_name}': {e}")
            continue
    
        # Extract date from the file name using regex
        match = re.search(r'(\d{1,2}_\d{1,2}_\d{4})', file_name)
        if match:
            date_str = match.group(1)
            try:
                # Convert the extracted date to a datetime object
                file_date = datetime.strptime(date_str, '%m_%d_%Y')
                # Create the subfolder name using the date
                subfolder_name = file_date.strftime('%m_%d_%Y')
                # Path to the remote subfolder
                remote_subfolder_path = os.path.join(remote_path, subfolder_name)
                # Create the remote subfolder if it doesn't exist
                try:
                    sftp.chdir(remote_subfolder_path)
                except FileNotFoundError:
                    sftp.mkdir(remote_subfolder_path)
                # Move the file to the remote subfolder
                remote_src_path = os.path.join(remote_path, file_name)
                remote_dst_path = os.path.join(remote_subfolder_path, file_name)
                sftp.rename(remote_src_path, remote_dst_path)
                print(f"Moved '{file_name}' to '{subfolder_name}'")
            except ValueError:
                print(f"Failed to process '{file_name}'")
    
    
    
    
    # Close the SFTP connection
    sftp.close()
    transport.close()
    

















































