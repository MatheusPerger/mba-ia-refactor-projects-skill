from flask import jsonify

from utils.clock import utc_now


def health():
    return jsonify({'status': 'ok', 'timestamp': str(utc_now())})


def index():
    return jsonify({'message': 'Task Manager API', 'version': '1.0'})
