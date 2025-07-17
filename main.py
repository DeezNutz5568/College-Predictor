from flask import Flask, request, jsonify, render_template, send_from_directory
import pymysql
from collections import defaultdict
import os

app = Flask(__name__)

# --- DB Config ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '5568',  # your db password
    'database': 'college_predictor',
    'cursorclass': pymysql.cursors.DictCursor
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

@app.route('/predict', methods=['GET'])
def predict():
    rank = int(request.args.get('rank', 0))
    category = request.args.get('category', '').upper()         # used as seat_stype
    gender = request.args.get('gender', '').lower()
    state = request.args.get('state', '').title()
    inst_type = request.args.get('institute_type', '').upper()

    # Connect to DB
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()

    # SQL Query
    sql = """
        SELECT * FROM college_data
        WHERE closing_rank >= %s
        AND seat_stype = %s
        AND (gender_type = 'Gender-Neutral' OR gender_type = %s)
    """
    params = [rank, category, 'Female' if gender == 'female' else 'Gender-Neutral']

    if inst_type:
        sql += " AND institute_type = %s"
        params.append(inst_type)

    cursor.execute(sql, params)
    results = cursor.fetchall()
    connection.close()

    # Group results
    grouped = defaultdict(lambda: {
        'institute': '',
        'image_url': '',
        'programs': []
    })

    for row in results:
        name = row['institute_name']
        grouped[name]['institute'] = name
        grouped[name]['image_url'] = f"/images/{name.lower().replace('&', 'and').replace(' ', '_').replace(',', '').replace('.', '')}.jpg"
        grouped[name]['programs'].append({
            'program': row['academic_program'],
            'closing_rank': row['closing_rank']
        })

    return jsonify(list(grouped.values()))

if __name__ == '__main__':
    app.run(debug=True)
