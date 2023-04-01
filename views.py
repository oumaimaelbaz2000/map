
    import folium
    import numpy as np
    from folium import plugins
    from osgeo import gdal
    import geopandas as gpd
    import glob



    # Get Central point
    centerx = -6.0610576389999995
    centery = 34.2434786915

    # Visualization in folium
    m = folium.Map(location=[centery, centerx], zoom_start=13.5, tiles='OpenStreetMap', zoom_control=True,
                   dragging=False, min_zoom=13, max_zoom=18, no_touch=True)




    # Add MousePosition plugin to display coordinates
    plugins.MousePosition().add_to(m)

    # display the map with the HTML code


    list_of_files = glob.glob('coordinates_*.txt')
    latest_file = max(list_of_files, key=os.path.getctime)
    data = np.loadtxt(latest_file, delimiter=';')
    print(data.shape)
    print(data)
    data = data[:, ::-1]
    # Extract longitudes and latitudes
    lons = data[:, 0]
    lats = data[:, 1]
    folium.PolyLine(locations=list(zip(lats, lons)), color='red', weight=3).add_to(m)
    start_point = (lats[0], lons[0])
    end_point = (lats[-1], lons[-1])
    folium.Marker(location=start_point, icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(location=end_point, icon=folium.Icon(color='red')).add_to(m)
    # Save html
    m.save('polls/templates/polls/drone.html')

