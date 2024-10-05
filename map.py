import folium

def create_map():
    m = folium.Map(location=[51.0447, -114.0719], zoom_start=12)
    folium.Marker([51.0447, -114.0719], popup="Calgary").add_to(m)
    m.save('templates/map.html')
