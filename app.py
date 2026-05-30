# app.py — Flask dashboard dla monitoringu ruchu drogowego w Opolu

from flask import Flask, render_template, request, jsonify
import logging

from traffic_api import fetch_current_traffic
from db_utils import get_connection, init_db
from logger_config import setup_logging

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/traffic", methods=["POST"])
def traffic():
    data = request.get_json(force=True)
    lat = data.get("lat")
    lon = data.get("lon")

    if lat is None or lon is None:
        return jsonify({"error": "Brak współrzędnych lat/lon"}), 400

    try:
        lat = float(lat)
        lon = float(lon)
    except (TypeError, ValueError):
        return jsonify({"error": "Nieprawidłowe współrzędne"}), 400

    records = fetch_current_traffic(lat=lat, lon=lon)
    if not records:
        return jsonify({"error": "Brak danych z API TomTom"}), 502

    return jsonify(records[0])


@app.route("/api/history")
def history():
    limit = request.args.get("limit", 20, type=int)
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT timestamp, lat, lon, speed, speed_limit, jam_factor, confidence "
            "FROM traffic ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )
        rows = cur.fetchall()
        cols = ["timestamp", "lat", "lon", "speed", "speed_limit", "jam_factor", "confidence"]
        return jsonify([dict(zip(cols, row)) for row in rows])
    finally:
        conn.close()


if __name__ == "__main__":
    setup_logging()
    init_db()
    app.run(debug=True, port=5000)
