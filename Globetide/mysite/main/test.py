import csv
import os
import chardet
from unidecode import unidecode

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

base_path = os.path.join('static', 'main')

csv_files = ['countries.csv']

def read_csv_file_count(file_path):
    print(f"Reading file: {file_path}") 
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    country_dict = {}
    
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            name = row.get('name', '').strip()  
            country_dict[name] = {
                'iso3': row.get('iso3', '').strip(),
                'phone_code': row.get('phone_code', '').strip(),
                'currency': row.get('currency', '').strip(),
                'capital': row.get('capital', '').strip(),
                'country_coordinates': (row.get('latitude', '').strip(), row.get('longitude', '').strip())
            }
    
    return country_dict

for file_name in csv_files:
    file_path = os.path.join(base_path, file_name)
    country_data = read_csv_file_count(file_path)


def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        rawdata = f.read()
    return chardet.detect(rawdata)['encoding']

encoding = detect_encoding(os.path.join(base_path, 'cities.csv'))


def append_cities_to_countries(countries_dict, cities_file_path):
    with open(cities_file_path, mode='r', newline='', encoding=encoding) as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            country_name = unidecode(row.get('country_name', '').strip())
            city_name = unidecode(row.get('name', '').strip())
            coordinates = (row.get('latitude', '').strip(), row.get('longitude', '').strip())
            
            if country_name in countries_dict:
                if 'cities' not in countries_dict[country_name]:
                    countries_dict[country_name]['cities'] = []
                countries_dict[country_name]['cities'].append((city_name, coordinates))


countries_dict = country_data
cities_file_path = os.path.join(base_path, 'cities.csv')
append_cities_to_countries(countries_dict, cities_file_path)



