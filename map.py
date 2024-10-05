import folium
import json
from folium.plugins import Draw

def create_map():
    # Create base map centered on Calgary with limited bounds (adjust coordinates for exact city bounds)
    m = folium.Map(
        location=[51.0447, -114.0719], 
        zoom_start=12,
        max_bounds=True,
        max_lat=51.3, min_lat=50.8, max_lon=-113.8, min_lon=-114.4  # Approx bounds for Calgary
    )

    # Add ArcGIS World Imagery
    folium.TileLayer(
        tiles="https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="ArcGIS Satellite Imagery",
        overlay=True,
        control=True
    ).add_to(m)

    # Add Calgary's boundary using a GeoJSON file (with UTF-8 encoding)
    with open('static/calgary_boundary.geojson', encoding='utf-8') as f:
        geojson_data = json.load(f)
    folium.GeoJson(geojson_data, name='Calgary Boundary').add_to(m)

    # Add lasso tool using Leaflet Draw
    draw = Draw(export=True)
    draw.add_to(m)

    # Add Layer Control
    folium.LayerControl().add_to(m)

    # Save map to HTML
    m.save('templates/map.html')
