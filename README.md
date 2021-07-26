# CyberSite

---
## Installation Instructions

1. Install Python 3
2. Install the virtualenv package
    - `pip install virtualenv`
3. Clone this repository
    - `git clone git@github.com:harrhunt/CyberSite.git`
4. Create the virtual environment inside the cloned repository
    - `virtualenv env`
5. Start the virtual environment
    1. Linux
        - `source env/bin/activate`
    2. Windows
        - `env\Scripts\activate.bat`
6. Install the dependencies
    - `pip install -r requirements.txt`
7. While still in the virtual environment, start the Flask app with Gunicorn 
    - `gunicorn --bind 127.0.0.1:5000 app:app`
        - (*This is for a local instance*)
        - For setting up with your server, check out this reference 
            - [How To Serve Flask Applications with Gunicorn and Nginx on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04)
8. Navigate to http://localhost:5000 to view the project