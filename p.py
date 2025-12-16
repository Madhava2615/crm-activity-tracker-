
from flask import Flask, request, jsonify # type: ignore
from flask_cors import CORS # type: ignore
import sqlite3
import datetime


app = Flask(__name__)
CORS(app)


def init_db():
    conn = sqlite3.connect('crm_activities.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS activities
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  type TEXT,
                  contact_name TEXT,
                  date TEXT,
                  duration INTEGER,
                  notes TEXT,
                  closed BOOLEAN DEFAULT FALSE,
                  closed_date TEXT)''')
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return "CRM Backend is running"


@app.route('/activities', methods=['GET'])
def get_activities():
    conn = sqlite3.connect('crm_activities.db')
    c = conn.cursor()
    c.execute('SELECT * FROM activities ORDER BY date DESC')
    rows = c.fetchall()
    
    activities = []
    for row in rows:
        activities.append({
            'id': row[0],
            'type': row[1],
            'contactName': row[2],
            'date': row[3],
            'duration': row[4],
            'notes': row[5],
            'closed': bool(row[6]),
            'closedDate': row[7]
        })
    
    conn.close()
    return jsonify(activities)

@app.route('/activities', methods=['POST'])
def add_activity():
    data = request.json
    conn = sqlite3.connect('crm_activities.db')
    c = conn.cursor()
    c.execute('''INSERT INTO activities 
                 (type, contact_name, date, duration, notes)
                 VALUES (?, ?, ?, ?, ?)''',
              (data['type'], data['contactName'], data['date'],
               data['duration'], data['notes']))
    conn.commit()
    conn.close()
    return jsonify({'success': True}), 201

@app.route('/activities/<int:activity_id>', methods=['PATCH'])
def toggle_activity(activity_id):
    action = request.json.get('action')
    conn = sqlite3.connect('crm_activities.db')
    c = conn.cursor()
    
    if action == 'toggle_close':
        c.execute('SELECT closed FROM activities WHERE id = ?', (activity_id,))
        current_closed = c.fetchone()
        if current_closed:
            closed = not bool(current_closed[0])
            closed_date = datetime.datetime.now().isoformat() if closed else None
            c.execute('UPDATE activities SET closed = ?, closed_date = ? WHERE id = ?',
                     (closed, closed_date, activity_id))
    elif action == 'delete':
        c.execute('DELETE FROM activities WHERE id = ?', (activity_id,))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
