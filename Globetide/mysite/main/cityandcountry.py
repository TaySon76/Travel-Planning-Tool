import csv
import os
from unidecode import unidecode
import chardet
import string

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

base_path = os.path.join('static', 'main')

csv_files = ['citiesandcountries.csv']

printable = set(string.printable)

def escape_quotes_in_string(s):
    """Escape double quotes in a string for safe literal_eval."""
    return s.replace('"', '\\"')

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        rawdata = f.read()
    return chardet.detect(rawdata)['encoding']

def is_printable(s):
    """Check if a string is printable, including accented characters."""
    return all(char in printable or char.isprintable() for char in s)

def read_csv_file(file_path):
    print(f"Reading file: {file_path}")
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return {}
    
    output_file = os.path.join(base_path, 'output.txt')
    
    try:
        with open(output_file, 'w', encoding='utf-8') as output:
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                for row_num, row in enumerate(csv_reader, start=1):
                    filtered_row = {key: ''.join(filter(is_printable, value)) for key, value in row.items()}
                    country = unidecode(filtered_row.get('country', '').strip())  
                    city = unidecode(filtered_row.get('city', '').strip())
                    
                    output.write(f"{country}: {city}\n")
                    print(f"Processed row {row_num}: {country} - {city}")
    
    except Exception as e:
        print(f"Error processing row {row_num}: {e}")

    return output_file
 
file_path = os.path.join(base_path, 'citiesandcountries.csv')
output_file = read_csv_file(file_path)
print(f"Processed data written to: {output_file}")
