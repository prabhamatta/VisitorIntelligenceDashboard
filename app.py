from flask import Flask, render_template, request, jsonify
import csv
import os
from user_agents import parse
from urllib.parse import urlparse

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
EXPECTED_COLUMNS = {"user_agent", "domain", "page_url", "referral_url"}  # Define required columns


def parse_user_agent(ua_string):
    ua = parse(ua_string)
    return {
        'browser': ua.browser.family,
        'os': ua.os.family,
        'device': 'Mobile' if ua.is_mobile else 'Tablet' if ua.is_tablet else 'Desktop'
    }

def extract_domain(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc == "":
        return "-" 
    else: 
        return parsed_url.netloc  # Extracts domain

def extract_first_two_path_parts(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    return '/'.join(path_parts[:2]) if len(path_parts) >= 2 else parsed_url.path

def validate_csv_format(file_path):
    """Checks if the uploaded file matches the expected sample data format."""
    try:
        with open(file_path, 'r', encoding='ISO-8859-1', errors='replace') as file:
            csv_reader = csv.reader(file)
            headers = next(csv_reader)  # Read the header row
            headers = {h.strip().lower().replace(" ", "_") for h in headers}  # Normalize column names
            
            missing_columns = EXPECTED_COLUMNS - headers
            if missing_columns:
                return False, f"Missing mandatory columns: {', '.join(missing_columns)}"
            
            return True, None
    except Exception as e:
        return False, str(e)

def get_latest_uploaded_file():
    """Retrieves the most recently uploaded CSV file."""
    files = [os.path.join(UPLOAD_FOLDER, f) for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.csv')]
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)  # Get the latest file by creation time
    return latest_file

def read_csv_file(file_path):
    data = []
    headers = []
    unique_domains, unique_pages, unique_browsers, unique_os, unique_devices, unique_referrals = set(), set(), set(), set(), set(), set()
    
    try:
        with open(file_path, 'r', encoding='ISO-8859-1', errors='replace') as file:
            first_line = file.readline().replace('\x00', '').strip()
            csv_reader = csv.reader([first_line] + file.readlines())
            
            headers = next(csv_reader)  # Read the header row
            headers = [h.strip().lower().replace(" ", "_") for h in headers]  # Normalize column names
            
            print(f"Headers read from file: {headers}")  # Debugging output
            
            for row in csv_reader:
                if len(row) == len(headers):
                    row_dict = dict(zip(headers, row))
                    
                    # Extracting and storing unique values
                    if 'user_agent' in row_dict:
                        ua_info = parse_user_agent(row_dict['user_agent'])
                        row_dict.update(ua_info)
                        unique_browsers.add(ua_info['browser'])
                        unique_os.add(ua_info['os'])
                        unique_devices.add(ua_info['device'])
                    
                    if 'domain' in row_dict and row_dict['domain'].strip():
                        unique_domains.add(row_dict['domain'].strip())

                    if 'page_url' in row_dict and row_dict['page_url'].strip():
                        normalized_page_url = extract_first_two_path_parts(row_dict['page_url'].strip())
                        unique_pages.add(normalized_page_url)
                        row_dict['page_url'] = normalized_page_url  # Normalize the page URL in the dataset

                    if 'referral_url' in row_dict and row_dict['referral_url'].strip():
                        referral_domain = extract_domain(row_dict['referral_url'].strip())
                        unique_referrals.add(referral_domain)
                        row_dict['referral_url'] = referral_domain  # Normalize referral domain in dataset
               
                    data.append(row_dict)
        
        print(f"Total records read: {len(data)}")  # Debugging output

        return headers, data, unique_domains, unique_pages, unique_browsers, unique_os, unique_devices, unique_referrals, None
    except Exception as e:
        return None, None, None, None, None, None, None, None, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        is_valid, error_message = validate_csv_format(file_path)
        print(f"File validation result: {is_valid}, {error_message}")  # Debugging output
        if not is_valid:
            return jsonify({'message': f'Invalid file format: {error_message}'}), 400

        headers, data, unique_domains, unique_pages, unique_browsers, unique_os, unique_devices, unique_referrals, error = read_csv_file(file_path)
        if error:
            return jsonify({'error': error}), 400
        print(f"Available keys in first record: {data[0].keys() if data else 'No data found'}")  # Debugging output

        return jsonify({
            'domains': sorted(unique_domains),
            'pages': sorted(unique_pages),
            'browsers': sorted(unique_browsers),
            'os':  sorted(unique_os),
            'devices': sorted(unique_devices),
            'referrals': sorted(unique_referrals),
            'message': 'File uploaded successfully'
        })
    return jsonify({'message': 'No file uploaded'}), 400


@app.route('/filter', methods=['POST'])
def filter_data():
    filters = request.json
    file_path = get_latest_uploaded_file()
    if not file_path:
        return jsonify({'error': 'No valid CSV file found'}), 400
    
    print(f"Filtering data from file: {file_path}")  # Debugging output
    headers, data, _, _, _, _, _, _, error = read_csv_file(file_path)
    if error:
        return jsonify({'error': error}), 400
    
    filtered_data = []
    for row in data:
        match = True
        for key, value in filters.items():
            if value and value != "All":  # Ignore empty and "All" values
                row_value = row.get(key.replace(" ", "_").lower(), "").strip().lower()
                # row_value = row.get(key, "").strip().lower()
                if key == "page":
                    row_value = row.get('page_url', "").strip().lower() 
                elif key == "referral":
                    row_value = row.get('referral_url', "").strip().lower() 
                else:
                    row_value = row.get(key, "").strip().lower()      
                    # row_value = row.get(key, "").strip().lower() if key != "page" else row.get('page url', "").strip().lower() 

                filter_value = value.strip().lower()
                if row_value != filter_value:
                    match = False
                    break  # Stop checking if one filter doesn't match
        if match:
            filtered_data.append(row)
    
    return jsonify(filtered_data) if filtered_data else jsonify({'message': 'No records found'})

if __name__ == '__main__':
    app.run(debug=True)
