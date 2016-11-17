API_KEY = 'key'
ENDPOINT = 'http://localhost:5001'
USERNAME = 'admin'
PASSWORD = 'secret'
SECRET_KEY = 'its-a-secret'
HOST = '0.0.0.0'
PORT = 5001
DEBUG = True
TESTING = True
WTF_CSRF_ENABLED = False
Z3950_DATABASES = {"loc": {"db": "Voyager", "host": "z3950.loc.gov",
                           "port": 7090}}
Z3950_URL = "/z3950/search/loc/"
ZIP_FOLDER = "/tmp/"
MATCH_PERCENTAGE = 60
EXCLUDED_KEYS = ['ip_address']
