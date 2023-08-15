# Capstone-Full-Back-End

## Description
The back-end is built using a Flask-Python app with pymongo to connect to the mongoDB database for the user routes. It also works as a proxy server to fetch data from the Rescue Group API.[ Click here for the front end.](https://github.com/aimo22/capstone-front-end)

## List of dependencies
- Flask
- Pymongo
- Flask_jwt_extended

## Instructions for setting up the App

1. Clone this repository locally:
   ```
   $ git clone [repository_url]
   ```

2. Open the project directory:
   ```
   $ cd capstone-full-back-end
   ```

3. Create a virtual environment:
   ```
   $ python -m venv venv
   ```

4. Activate the virtual environment:
     ```
    $ source venv/bin/activate
    ```

5. Install the required dependencies from the `requirements.txt` file:
   ```
   $ pip install -r requirements.txt
   ```

6. Start the Flask app:
   ```
   $ flask run
   ```