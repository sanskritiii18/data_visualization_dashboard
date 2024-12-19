from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['database']
collection = db['collection']


country_coordinates = {
    "United States of America": [-98.5795, 39.8283],
    "Brazil": [-51.9253, -14.2350],
    "Germany": [10.4515, 51.1657],
    "China": [104.1954, 35.8617],
    "Mexico": [-102.5528, 23.6345],
    "Lebanon": [35.8623, 33.8547],
    "Nigeria": [8.0820, 9.0820],
    "Russia": [105.3188, 61.5240],
    "Iran": [53.6880, 32.4279],
    "India": [78.9629, 20.5937],
    "Saudi Arabia": [45.0792, 23.8859],
    "Iraq": [43.6793, 33.2232],
    "Libya": [17.2283, 26.3351],
    "Indonesia": [113.9213, -0.7893],
    "Japan": [137.7261, 35.6762],
    "Egypt": [31.2357, 30.0444],
    "Canada": [-106.3468, 56.1304],
    "United Kingdom": [-3.4350, 55.3781],
    "Venezuela": [-66.5897, 6.4238],
    "Australia": [133.7751, -25.2744],


}

for document in collection.find():
    country = document.get('country')
    if country in country_coordinates:
        coordinates = country_coordinates[country]


        collection.update_one(
            {'_id': document['_id']},
            {'$set': {'location': {'type': 'Point', 'coordinates': coordinates}}}
        )#for updating the coordinates to plot on map