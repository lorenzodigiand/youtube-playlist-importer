# YouTube Playlist Importer

This script was created to import music playlists from any music streaming services to YouTube Music, there are already some sites which accomplish the same task but I wanted to make a free alternative.<br>
To run this script you'll need Python installed on your machine, a CSV file containing all your songs and a client_secret.json file as your credentials.

## Quick Start
### 1. Installing Pyhton and its libraries
The script is written in python, you can install Python from [here](https://www.python.org/downloads/).<br>
Then you'll need to install a few pip libraries, after installing Python open the terminal as an amministrator and run the following command.
```
pip install google-auth google-auth-oauthlib google-auth-httplib2 googleapiclient pandas
```
### 2. Export your playlist as a CSV file
Go to [TuneMyMusic](https://www.tunemymusic.com/) and login with your streaming service account, then select your playlist and export as a CSV file, unfortunately you can only export a maximum of 900 track but you can repeat this step multiple times and create a giant CSV file by merging them together.<br>
Rename the file to <b>playlist.csv</b>, after renaiming be sure that the CSV file contains only this 3 columns: <b>Track Name, Artist name, Album</b>; if there are any other columns you can get rid of them, they won't be necessary.

### 2. Get your API Credentials
To communicate with your YouTube account you'll need to get API credentials.<br>
Go to [Google Cloud Platform](https://console.cloud.google.com) and create a new project, give it any name you want and click on create.<br>
On the left menu go to <b>API and services</b> then go to <b>Library</b>, scroll down until you see <b>YouTube Data API v3</b> then click on add.<br>
Go back and go to <b>Credentials</b>, on the top click on <b>Create Credentials -> ID client OAuth</b>. You'll have to configure the login auth page, click on <b>external</b> and put all the info requested, choose <b>App Desktop</b> as your application type, give it any name you want then click on create.<br>
After creating your credentials you'll see on the right side of the screen a download button, click it to obtain your JSON file and rename it to <b>client_secret.json</b>. Now we have all we need to run the script.

### 3. Running the script
Create a folder anywhere you want on your disk and put all the files inside the folder, the file structure should be like this:
```
folder
├── script.py
├── playlist.csv
└── client_secret.json
```
If your file structure looks like this you can open your terminal, navigate to the folder and run this command:
```
python script.py
```
You'll get redirected to an authentication tab on your default browser, be sure to use a browser based on chromium (Chrome, Opera, Edge) cuase other browser give issues on this step (Firefox for example).<br>
After logging in with the same account you used for the authentication key it will say that this application is not verified by Google, it's natural since our project on the Google Cloud Platform is private, click on continue and give the application access to your YouTube Account.<br> 
After connecting successfully we'll be prompted to close our browser windows, meanwhile the script will start finding our songs and will put them in a new playlist on YouTube<br>
### The Downsides
Unfortunately due to the limitations of a free project on the Google Cloud Platform there is a certain limit of actions our scrpit can do using YouTube Data APIs, after reaching the quota of 10.000 actions per day the script will stop and we won't be able to use it until the next day, to circumvent this limit we'll be forced to modify our CSV file every day checking at which song the script stopped and continuing the next day from that point forward.
