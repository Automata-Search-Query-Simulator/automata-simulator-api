import os
from pathlib import Path
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
@app.route('/api/debug/fs')
def debug_fs():
    base = Path('/var/task')
    api_backend = base / 'api' / 'BACKEND'
    backend = base / 'BACKEND'
    paths = [base, api_backend, backend]
    listing = {}
    for p in paths:
        try:
            if p.exists():
                listing[str(p)] = sorted([f.name for f in p.iterdir()])
            else:
                listing[str(p)] = None
        except Exception as e:
            listing[str(p)] = f'error: {e}'
    return jsonify({
        'cwd': os.getcwd(),
        'paths': listing
    })
