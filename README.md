# I2CL

---
## Installation Instructions
1. Install Python 3
2. Install the virtualenv package
    - `pip install virtualenv`
3. Clone this repository
    - `git clone git@github.com:harrhunt/I2CL.git`
4. Create the virtual environment inside the cloned repository
    - `virtualenv env`

Follow the instructions pertaining to your OS

### Linux
5. Start the virtual environment
    - `source env/bin/activate`
6. Install the dependencies
    - `pip install -r lin-requirements.txt`
7. While still in the virtual environment, start the Flask app with Gunicorn 
    - `gunicorn --bind 127.0.0.1:5000 app:app`
        - (*This is for a local instance*)
        - For setting up with your server, check out this reference 
            - [How To Serve Flask Applications with Gunicorn and Nginx on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04)
8. Navigate to http://localhost:5000/ to view the project

### Windows
5. Start the virtual environment
    - `env\Scripts\activate.bat`
6. Install the dependencies
    - `pip install -r win-requirements.txt`
7. While still in the virtual environment, start the Flask app with Gunicorn 
    - `waitress-serve --listen=*:8000 app:app`
        - (*This is for a local instance*)
8. Navigate to http://localhost:8000/ to view the project

# Editing Site Theme

All site colors are defined and imported from the `static/styles/sass/_variables.sass` file. To edit the site theme, change out the `$primary-color` and `$secondary-color` variables with the desired hex or RGB code. The rest of the site colors are drawn from the various variables named as shades of black, gray, and white.

The logos are placed in the navbar in the `templates/base.html` file. To change any of the logos, simply add the new logo to the `static/images/` folder and replace the filename of the old logo with the filename of the new logo.

# Future Plans

Here are some of the future plans for this project that will hopefully be completed by whoever takes up the torch

- Completion of the Admin section for adding to and editing the data in the database
- Better search capabilities (better matching and/or fuzzy search)
- Breadcrumb navigation style filtering (choose a knowledge area -> choose a knowledge unit)
- Add pagination to the module search route
