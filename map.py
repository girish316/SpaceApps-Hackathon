import folium
import json
from folium.plugins import Draw

def create_map():
    # Create base map centered on Calgary
    m = folium.Map(
        location=[51.0447, -114.0719], 
        zoom_start=12,
        control_scale=True,
        tiles=None  # Prevents default OpenStreetMap layer from being loaded
    )

    # Add ArcGIS World Imagery as the default layer
    folium.TileLayer(
        tiles="https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="ArcGIS Satellite Imagery",
        overlay=True,
        control=True
    ).add_to(m)

    # Add OpenStreetMap tile layer (optional)
    folium.TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        name="OpenStreetMap",
        attr="&copy; OpenStreetMap contributors",
        overlay=False  # Not enabled by default
    ).add_to(m)

    # Add lasso tool
    draw = Draw(export=True)
    draw.add_to(m)

    # Load the GeoJSON file for crime data
    geojson_path = 'static/all_communities_aggregated.geojson'
    with open(geojson_path, 'r', encoding='utf-8') as f:
        all_communities_geojson = json.load(f)

    # Get crime data and color scaling
    crime_counts = [feature['properties']['Crime Count'] for feature in all_communities_geojson['features']]
    mean_crime = sum(crime_counts) / len(crime_counts)

    def get_color(crime_count):
        if crime_count > mean_crime:
            return 'red'
        elif crime_count > (mean_crime / 2):
            return 'orange'
        else:
            return 'green'

    # Add crime heatmap
    folium.GeoJson(
        all_communities_geojson,
        style_function=lambda feature: {
            'fillColor': get_color(feature['properties']['Crime Count']),
            'color': 'transparent',
            'weight': 0,
            'fillOpacity': 0.6
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['Community', 'Crime Count'],
            aliases=['Community: ', 'Total Crimes: '],
            localize=True
        ),
        name="Crime Heatmap",
        overlay=True
    ).add_to(m)

    # Load the traffic data from GeoJSON
    traffic_geojson_path = 'static/traffic_2023.geojson'
    with open(traffic_geojson_path, 'r', encoding='utf-8') as f:
        traffic_geojson = json.load(f)

    # Fix field names: replace spaces with underscores
    for feature in traffic_geojson['features']:
        feature['properties']['Section_Name'] = feature['properties'].pop('Section Name')
        feature['properties']['Traffic_Volume'] = feature['properties'].pop('Volume')

    # Function to define line color and weight based on traffic volume
    def get_traffic_style(volume):
        if volume > 122016:
            return {'color': '#5A2A8E', 'weight': 15}  # Purple
        elif volume > 92512:
            return {'color': '#2F5FA0', 'weight': 12}  # Dark Blue
        elif volume > 63008:
            return {'color': '#4AA9E4', 'weight': 9}  # Moderate Blue
        elif volume > 33504:
            return {'color': '#7FC3EB', 'weight': 6}  # Sky Blue
        else:
            return {'color': '#B3DDF2', 'weight': 3}  # Light Blue

    # Add the traffic data layer to the map with gradient coloring
    folium.GeoJson(
        traffic_geojson,
        name="Traffic Volume Flow",
        style_function=lambda feature: get_traffic_style(feature['properties']['Traffic_Volume']),
        tooltip=folium.GeoJsonTooltip(
            fields=['Section_Name', 'Traffic_Volume'],  # Use sanitized field names
            aliases=['Road Section', 'Traffic Volume']
        )
    ).add_to(m)

    # Add Layer Control to switch between layers
    folium.LayerControl().add_to(m)

    # Add custom legend for traffic volume ranges
    legend_html = '''
     <div style="position: fixed; 
     bottom: 50px; left: 50px; width: 250px; height: 200px; 
     background-color: white; border:2px solid grey; border-radius: 8px; padding: 10px; z-index:9999; font-size:14px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
     
     <!-- Title with unique background color -->
     <div style="background-color: #4AA9E4; color: white; padding: 8px; text-align: center; font-weight: bold; border-radius: 5px; margin-bottom: 10px;">
     Traffic Volumes for 2023
     </div>
     
     <!-- Legend content with new color scheme -->
     <div style="display: flex; align-items: center; margin-bottom: 6px;">
        <div style="background-color: #5A2A8E; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> 122,016 - 151,520
     </div>
     <div style="display: flex; align-items: center; margin-bottom: 6px;">
        <div style="background-color: #2F5FA0; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> 92,512 - 122,016
     </div>
     <div style="display: flex; align-items: center; margin-bottom: 6px;">
        <div style="background-color: #4AA9E4; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> 63,008 - 92,512
     </div>
     <div style="display: flex; align-items: center; margin-bottom: 6px;">
        <div style="background-color: #7FC3EB; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> 33,504 - 63,008
     </div>
     <div style="display: flex; align-items: center;">
        <div style="background-color: #B3DDF2; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> 4,000 - 33,504
     </div>

     </div>
     '''


    m.get_root().html.add_child(folium.Element(legend_html))

    # Save the map to HTML
    m.save('templates/map.html')

