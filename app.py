import sqlite3
import os
import string
from flask import Flask, render_template, request, url_for, g, jsonify, abort, send_from_directory

app = Flask(__name__)

DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "dumbdash.db")
os.makedirs(DATA_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT, hostname TEXT, cpus INTEGER,
            ram INTEGER, rootdisksize INTEGER, pubip TEXT, privip TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (id INTEGER, hostname TEXT, service TEXT, status TEXT)
    ''')
    conn.commit()
    conn.close()
    print("Database intialised.")


init_db()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_FILE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None: db.close()

# --- Routes ---
# Homepage
@app.route('/')
def index(): return render_template('index.html')

@app.route('/sw.js')
def service_worker(): return send_from_directory('.', 'sw.js')

@app.route('/favicon.ico')
def favicon(): return send_from_directory('static/icons', 'icon-192x192.png')

# --- API Routing ---


@app.route('/api/stats', methods=['GET'])
def get_stats():
    db = get_db()
    total_devices = db.execute('SELECT COUNT(*) FROM devices').fetchone()[0] or 0
    return jsonify({'total_devices': total_devices})

@app.route('/api/update', methods=['POST'])
def update_api():
    data = request.get_json()
    if not data or 'hostname' not in data:
        return jsonify({'error': 'Bad request.'}), 400

    hostname = data['hostname']
    cpus = data['cpus']
    ram = data['ram']
    rootdisksize = data['rootdisksize']
    pubip = data['pubip']
    privip = data['privip']


    db = get_db()
    existing_device = db.execute('SELECT id FROM devices WHERE hostname = ?', (hostname,)).fetchone()
    if existing_device:
        print("Existing device.")
        id = existing_device['id']
        cursor = db.execute('UPDATE devices SET hostname = ?, cpus = ?, ram = ?, rootdisksize = ?, pubip = ?, privip = ? WHERE id = ?', (hostname, cpus, ram, rootdisksize, pubip, privip, id))
        db.commit()
    else:
        cursor = db.execute('INSERT INTO devices (hostname, cpus, ram, rootdisksize, pubip, privip) VALUES (?, ?, ?, ?, ?, ?)', (hostname, cpus, ram, rootdisksize, pubip, privip))
        db.commit()
    return jsonify({'status': 'Success.'}), 200


@app.route('/api/devices', methods=['GET'])
def get_devices():
    db = get_db()
    devices = db.execute('SELECT id, hostname, cpus, ram, rootdisksize, pubip, privip FROM devices ORDER BY hostname ASC').fetchall()
    return jsonify([dict(row) for row in devices])

@app.route('/api/services', methods=['GET'])
def get_services():
    db = get_db()
    services_row = db.execute('SELECT hostname, service, status FROM services').fetchone()

@app.route('/api/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    db = get_db()
    db.execute('DELETE FROM devices WHERE id = ?', (device_id,))
    db.commit()
    return jsonify({'success': True})

@app.errorhandler(404)
def not_found_error(error):
    if request.path.startswith('/api/'): return jsonify({'error': 'Not Found'}), 404
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

