# I2CL

---
## Installation Instructions
1. Install Python 3
2. Install the virtualenv package
    - `pip install virtualenv`
3. Clone this repository
    - `git clone git@github.com:harrhunt/CyberSite.git`
4. Create the virtual environment inside the cloned repository
    - `virtualenv env`

Follow the instructions pertaining to your OS

### Linux
5. Start the virtual environment
    - `source env/bin/activate`
6. Install the dependencies
    - `pip install -r lin-requirements.txt`
7. While in the virtual environment, run `flask initdb` to create and initialize the database
8. While still in the virtual environment, start the Flask app with Gunicorn 
   - `gunicorn --bind 127.0.0.1:5000 app:app`
      - (*This is for a local instance*)
      - For setting up with your server, check out this reference 
        - [How To Serve Flask Applications with Gunicorn and Nginx on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04)
9. Navigate to http://localhost:5000/ to view the project

### Windows
5. Start the virtual environment
    - `env\Scripts\activate.bat`
6. Install the dependencies
    - `pip install -r win-requirements.txt`
7. While in the virtual environment, run `flask initdb` to create and initialize the database
8. While still in the virtual environment, start the Flask app with Waitress 
    - `waitress-serve --listen=*:8000 app:app`
        - (*This is for a local instance*)
9. Navigate to http://localhost:8000/ to view the project

## Database Configuration
1. Create or modify the `flaskconf.py` file
2. At the top of the file, make sure to set the configuration you want to use to a variable named `SELECTED_CONFIG`
   - e.g. `SELECTED_CONFIG = "flaskconf.TestingConfig"` where `flaskconf` is the name of the configuration file and `TestingConfig` is the name of the configuration class

## TODO
- Add ability to select and edit modules
- Add ability to delete modules
- ~~Fix wrapping of long file names on file section~~
- ~~Fix search on admin edit, so it doesn't redirect to regular module search~~
- Fix order by of modules when querying from the database
- Consider adding pagination to module results to allow for large database of modules