from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import json  # Import json module to work with JSON files

# Initialize the Flask app
app = Flask(__name__, static_folder='public')
CORS(app)  # This will allow cross-origin requests to your Flask app

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/data.json')
def data_file():
    return send_from_directory('public', 'data.json')

@app.route('/scrape')
def scrape_by_date():
    date = request.args.get('date')
    if not date:
        return jsonify({"error": "Date parameter is required (dd-mm-yyyy)"}), 400

    url = f"https://cmwssb.tn.gov.in/lake-level?date={date}"
    response = requests.get(url)

    if response.status_code == 200:
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table')
            
            if not table:
                return jsonify({"error": "No table found on page. Check if the page structure has changed."}), 500

            df = pd.read_html(str(table))[0]
            data = df.to_dict(orient='records')

            # Log the data for debugging
            print(f"Scraped data: {data}")

            # Write the fetched data to data.json
            with open('public/data.json', 'w') as json_file:
                json.dump(data, json_file, indent=4)

            return jsonify(data)

        except Exception as e:
            return jsonify({"error": f"Failed to parse data: {str(e)}"}), 500
    else:
        return jsonify({"error": f"Failed to fetch page. Status code: {response.status_code}"}), 502

# Start the Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
