import configparser

config = configparser.ConfigParser()
config.read('config.ini')

def get_database_names():
    return config['databases']

def get_centre_coords():
    return (float(config['activities']['centre_lat']), float(config['activities']['centre_long']))

def get_max_pages():
    return int(config['activities']['max_pages'])

def get_per_page():
    return int(config['activities']['per_page'])