import folium

def create_map():
    # Create base map centered on Calgary
    m = folium.Map(location=[51.0447, -114.0719], zoom_start=12)

    # Add an ArcGIS World Imagery layer (Satellite imagery)
    folium.TileLayer(
        tiles="https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="ArcGIS Satellite Imagery",
        overlay=True,
        control=True
    ).add_to(m)

    # Add marker for Calgary
    folium.Marker([51.0447, -114.0719], popup="Calgary").add_to(m)

    # Save the map as an HTML file
    m.save('templates/map.html')
