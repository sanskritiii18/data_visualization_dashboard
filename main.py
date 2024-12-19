import json
import folium
from folium.plugins import MarkerCluster
import random

import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from flask_cors import CORS
import pandas as pd



app = Flask(__name__)
CORS(app)


client = MongoClient('mongodb://localhost:27017/')
db = client['database']
collection = db['collection']

@app.route('/')
def two():
    return render_template("index.html")


@app.route("/map")
def mapping():
    base_map = folium.Map(location=[40.5862, -98.3899], zoom_start=10)
    marker_cluster = MarkerCluster().add_to(base_map)

    data = collection.find({})

    for record in data:

        coordinates = record.get('location', {}).get('coordinates', [])

        if isinstance(coordinates, list) and len(coordinates) == 2:

            lat = coordinates[1] + random.uniform(-1.0, 1.0)
            lon = coordinates[0] + random.uniform(-1.0, 1.0)
        else:
            continue


        sector = record.get('sector', 'Unknown Sector')
        topics = record.get('topic', 'No Topic')
        title = record.get('title', 'No Title')
        insight = record.get('insight', 'No Insight')


        if sector == 'Energy':
            color = 'blue'
        elif sector == 'Manufacturing':
            color = 'green'
        elif sector == 'Retail':
            color = 'red'
        elif sector == 'Support services':
            color = 'pink'
        else:
            color = 'gray'


        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(
                f"<strong>{title}</strong><br>{insight}<br>{topics}<br>{sector}",
                max_width=300
            ),
            icon=folium.Icon(color=color)
        ).add_to(marker_cluster)


    base_map.save('static/map.html') #for a base map on which after fetching data from database(mongodb ) we will plot on the map
    return render_template('map.html')


@app.route("/plot", methods=["POST"])
def plot():
    sector = request.json.get('sector', '')
    data1 = list(
        collection.find({"sector": {"$regex": f"^{sector}$", "$options": "i"}},
                        {"_id": 0, "start_year": 1,"intensity": 1, "sector": 1}))
    df = pd.DataFrame(data1)
    if df.empty:
        return jsonify({"error": "No data available for the selected sector"})
    df["start_year"] = pd.to_numeric(df["start_year"], errors="coerce")


    df_melted = df.melt(id_vars=["sector", "intensity"],
                        value_vars=["start_year"],
                        var_name="year_type",
                        value_name="year").dropna()
    df_melted = df_melted.sort_values("year")

    fig = px.line(df_melted,
                  x="year",
                  y="intensity",
                  title=f"Intensity Over Time for {sector.capitalize()} Sector",
                  labels={"year": "Year", "intensity": "Intensity"},
                  markers=True)
    fig.update_traces(mode="lines+markers")

    graph_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    return jsonify({"graph": graph_json})



@app.route('/pie-chart', methods=["GET","POST"])
def piechart():
    data = request.get_json()
    sector = data.get("sector")

    data2 = list(
        collection.find({"sector": sector},
                        {"_id": 0, "topic": 1, "likelihood": 1, "sector": 1}))

    df = pd.DataFrame(data2)
    df = df[df['likelihood'].notna() & (df['likelihood'] != '')]

    if df.empty:
        return jsonify({"error": "No data available for the selected sector with valid likelihood values"})

    pie_data = {}

    for index, row in df.iterrows():
        topic = row['topic']
        likelihood = row['likelihood']

        if topic in pie_data:
            pie_data[topic] += likelihood
        else:
            pie_data[topic] = likelihood


    return jsonify({"pie_data": pie_data})

@app.route('/relevance-pie-chart', methods=["POST"])
def relevance_piechart():
    data = request.get_json()
    sector = data.get("sector")

    data2 = list(
        collection.find({"sector": sector},
                        {"_id": 0, "topic": 1, "relevance": 1, "sector": 1}))
    df = pd.DataFrame(data2)


    df = df[df['relevance'].notna() & (df['relevance'] != '')]


    if df.empty:
        return jsonify({"error": "No data available for the selected sector with valid relevance values"})
    pie_data = {}
    for index, row in df.iterrows():
        topic = row['topic']
        relevance = row['relevance']

        if topic in pie_data:
            pie_data[topic] += relevance
        else:
            pie_data[topic] = relevance

    return jsonify({"pie_data": pie_data})


if __name__ == '__main__':
    app.run(debug=True)
