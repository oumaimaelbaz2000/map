import glob
import os
import threading
import time

import cv2
import numpy as np
from PIL import Image
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from .models import Camera
from .forms import CameraForm
from django.contrib.auth.decorators import login_required
#from .decorator import allowed_users, admin_only
from django.contrib.auth.models import Group



def home(request):
    if request.user.is_authenticated:

        return render(request, 'polls/home.html')
    else:

        messages.warning(request, "You must be logged in to access this page.")
        return redirect('login')


import threading
import time
import cv2
import numpy as np
from PIL import Image
from django.shortcuts import render, redirect
from .forms import CameraForm
from .models import Camera

import threading
import time
import cv2
import numpy as np
from PIL import Image
from django.shortcuts import render, redirect
from .forms import CameraForm
from .models import Camera

frames = {}


def capture_stream(camera):
    global frames
    # frame_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    # frame_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # fps = int(camera.get(cv2.CAP_PROP_FPS))
    # out = cv2.VideoWriter(f"camera_{id(camera)}.avi", cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), fps,
    #                     (frame_width, frame_height))
    while True:
        ret, frame = camera.read()
        if not ret:
            print(f"Error reading from camera {camera}")
            break

        # Process the frame
        img = Image.fromarray(frame)
        resized = img.resize((400, 400))
        resized_frame = np.array(resized)

        # Store the frame
        frames[str(camera)] = resized_frame

        # Write the frame to the video file
    # out.write(frame)
    camera.release()
    # out.release()


def capture_streams(camera_type, camera_urls):
    cameras = []
    for url in camera_urls:
        camera = cv2.VideoCapture(url)
        if not camera.isOpened():
            print(f"Error opening camera at {url}")
            continue
        cameras.append(camera)

    if not cameras:
        print("No cameras available!")
        return

    threads = []
    for camera in cameras:
        thread = threading.Thread(target=capture_stream, args=(camera,))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    while True:
        # Concatenate the frames from all cameras
        hori_frames = []
        for camera in cameras:
            if str(camera) in frames:
                hori_frames.append(frames[str(camera)])
        if not hori_frames:
            print("No frames available!")
            continue
        hori = np.concatenate(hori_frames, axis=1)

        # Display the concatenated frames
        cv2.namedWindow(camera_type, cv2.WINDOW_NORMAL)
        cv2.imshow(camera_type, hori)
        cv2.resizeWindow(camera_type, 1700,
                         600)  # Remplacer 1000 et 600 par les dimensions souhaitées pour votre fenêtre

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    for camera in cameras:
        camera.release()
    time.sleep(1)
    cv2.destroyAllWindows()


def stream(request):
    if request.user.is_authenticated:

        if request.method == 'POST':
            form = CameraForm(request.POST)
            if form.is_valid():
                camera = form.save()
                return redirect('camera.html')
        else:
            form = CameraForm()
        cameras = Camera.objects.all()
        camera_types = dict(Camera.CAMERA_TYPES)

        # Group cameras by type
        cameras_by_type = {}
        for camera in cameras:
            cameras_by_type.setdefault(camera.get_camera_type_display(), []).append(camera.url)

        if request.method == 'POST':
            camera_type = request.POST.get('camera_type')
            camera_urls = [camera.url for camera in cameras.filter(camera_type=camera_type)]
            stream_thread = threading.Thread(target=capture_streams, args=(camera_type, camera_urls))
            stream_thread.daemon = True
            stream_thread.start()

        return render(request, 'polls/camera.html',
                      {'form': form, 'cameras_by_type': cameras_by_type, 'camera_types': camera_types})
    else:
        messages.warning(request, "You must be logged in to access this page.")
        return redirect('login')




def add_camera(request, camera_type):
    if request.method == 'POST':
        form = CameraForm(request.POST)
        if form.is_valid():
            camera = form.save(commit=True)
            camera.ip_address = form.cleaned_data['ip_address']
            camera.url = f'rtsp://{camera.ip_address}/snap.jpg?JpegSize=M&JpegCam=1&JpegDomain=3560447&counter=1678781246243'
            camera.save()
            messages.success(request, 'Camera ajoutée avec succès.')
            return redirect('camera_list')


    else:
        form = CameraForm(initial={'camera_type': camera_type})
    return render(request, 'polls/add_camera.html', {'form': form})



def edit_camera(request, camera_id):
    camera = get_object_or_404(Camera, id=camera_id)

    if request.method == 'POST':
        form = CameraForm(request.POST, instance=camera)
        if form.is_valid():
            camera = form.save(commit=True)
            camera.url = f'rtsp://{camera.ip_address}/snap.jpg?JpegSize=M&JpegCam=1&JpegDomain=3560447&counter=1678781246243'

            camera.save()
            messages.success(request, 'Camera mise à jour avec succès.')
            return redirect('camera_list')
    else:
        form = CameraForm(instance=camera)

    return render(request, 'polls/edit_camera.html', {'form': form, 'camera': camera})



def delete_camera(request, camera_id):
    camera = get_object_or_404(Camera, id=camera_id)
    camera.delete()
    return redirect('camera_list')


@login_required

def camera_list(request):
    camera_types = dict(Camera.CAMERA_TYPES)
    cameras_by_type = {}

    for camera_type in camera_types.keys():
        cameras = Camera.objects.filter(camera_type=camera_type)
        cameras_by_type[camera_type] = cameras

    context = {
        'cameras_by_type': cameras_by_type,
        'request': request,
    }

    return render(request, 'polls/camera_list.html', context)

import json

def get_latest_coordinates(request):
    list_of_files = glob.glob('coordinates_*.txt')
    latest_file = max(list_of_files, key=os.path.getctime)
    data = np.loadtxt(latest_file, delimiter=';')
    data = data[:, ::-1]
    lons = data[:, 0]
    lats = data[:, 1]
    response_data = {'lats': list(lats), 'lons': list(lons)}
    return HttpResponse(json.dumps(response_data), content_type='application/json')

@login_required
def drone(request):
    import folium
    import numpy as np
    from folium import plugins
    from osgeo import gdal
    import geopandas as gpd
    import glob



    # Open raster file
    driver = gdal.GetDriverByName('GTiff')
    driver.Register()
    ds = gdal.Open('C:\\Bureau\\ai_pfe_2023\\QG\\Reprojected.tif')
    if ds is None:
        print('Could not open')

    # Get coordinates, cols and rows
    geotransform = ds.GetGeoTransform()
    cols = ds.RasterXSize
    rows = ds.RasterYSize

    # Get extent
    xmin = geotransform[0]
    ymax = geotransform[3]
    xmax = xmin + cols * geotransform[1]
    ymin = ymax + rows * geotransform[5]

    # Get Central point
    centerx = (xmin + xmax) / 2
    centery = (ymin + ymax) / 2


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


    return render(request, 'polls/drone_carte.html')


@login_required
def carte(request):
    return render(request, 'polls/carte.html')
