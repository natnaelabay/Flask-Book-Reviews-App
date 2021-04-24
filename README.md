# Booknest - A book reviews app with machine learning book recommendation 

> Booknest gives you an elegant UI to scroll through and search through book lists with the idea of providing reliable information about a book and an ML model for recommending books based on users age.

## Steps to get the application running
### Requirements
1. python3 with pip
2. an internet connection

### steps
1. create a virtual environment
    - `python -m venv venv`
    - `.\venv\Scripts\activate`
    - `pip install -r requirements.txt`
2. set the necessary environmental variables
    - `set DATABASE_URL=postgresql://tdyewcwridjnjh:cbf075ab7a87d57d5b851e0c5b389ed751aa2941fa75f7128567a5ab7f22a0c3@ec2-3-217-219-146.compute-1.amazonaws.com:5432/ded7d9rdhtgdjo`
    - `set FLASK_APP=app.py`


### info the herokupostgresql database might lag sometimes to resolve this create a new database and set the env variable as DATABASE_URL
    . you do not need to create the tables your self but make sure to open a terminal window in the directory of the project and set the FLASK_APP env variable and activate the virtual environment the 
    1. flask build-db -> this is for building the database
    3. python import.py

after these steps you will be able to run by using the command "flask run" the program with no problem!


















