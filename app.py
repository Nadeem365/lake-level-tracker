from flask import Flask, request, jsonify, send_from_directory
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

app = Flask(_name_, static_folder='public')

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
            df = pd.read_html(str(table))[0]
            data = df.to_dict(orient='records')
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": f"Failed to parse data: {str(e)}"}), 500
    else:
        return jsonify({"error": f"Failed to fetch page. Status code: {response.status_code}"}), 502

if _name_ == '_main_':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
