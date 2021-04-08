# About the application
    *to be included


# steps required to run the flask app

1. you need to have a fresh database or tables with names(users,books,reviews) will be dropped <br>

2. create a .env file and copy the data in .env.example and provide the necessary data 

## To install necessary packages
### windows
1. ``` python -m venv venv ``` <br>

2. ``` .\venv\Scripts\activate ```

3. ``` pip install -r requirements.txt``` <br>

### mac or linux

1. ``` virtualenv -p python3 . ``` <br>

2. ``` source bin/activate ``` <br>

3. ``` pip3 install -r requirements.txt``` <br>

## Create the Database schema
open your terminal with the virtualenv activated and run
1. ``` flask build-db ``` <br>

2. ```(mac/linux) python3 import.py  ``` <br>

3. ```(window) python import.py  ```

## Run the application
still the virtualenv needs to be activated <br>

``` flask run ```
