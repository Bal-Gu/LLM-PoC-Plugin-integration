# Description
The following project is a proof of concept to use multiple models to verify a message's integrity, privacy, and ethicality and prove a response if the criteria are met.

# Requirement
* Ollama
* Mysql
* Python 3.10
* Nodejs
* npm 9 or higher

# How to run
First make sure that the correct parameter are set in the config file of the backend.
There is also a second config file in the frontend incase you want to modify the backend URI.

#### Backend prerequisition
````shell
pip install -r requirements.txt
````
#### Backend run
Make sure that your working directory is pointing towards `backend` folder
````shell
python main.py
````

#### Frontend run
Before launching the frontend make sure that the backend is up and running.
Make sure that your working directory is pointing towards `frontend` folder
````shell
npm start
````