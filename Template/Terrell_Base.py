import bpy, bmesh
import math
import numpy as np
import csv
import datetime
import os

'''Defining Required Functions'''

def norm(vec):
    '''Function for calculating magnitude (norm) of a vector'''
    mag = 0
    for i in vec:
        mag+=i**2
    return math.sqrt(mag)

def Lorentz_Contract(obj_mesh):
    '''Function for taking object mesh as input and returning lorentz contracted mesh as output'''
    new_mesh = obj_mesh.copy()
    
    for points in new_mesh.verts:
        initial_pt = np.array([points.co.x, points.co.y, points.co.z])
        final_pt = initial_pt - ((g/(1+g))*(np.dot(initial_pt, beta)))*beta
        
        points.co.x = final_pt[0]
        points.co.y = final_pt[1]
        points.co.z = final_pt[2]
    
    return new_mesh

def Optical_Distort(obj_mesh, T):
    '''Function for taking object mesh as input and giving optically distorted version and centroid (relative to camera) of mesh as output according to the ct - coordinate specified by variable - T'''
    new_mesh = obj_mesh.copy()
    
    centroid = np.array([0.0,0.0,0.0])
    n = 0
    
    for points in new_mesh.verts:
        initial_pt = np.array([points.co.x, points.co.y, points.co.z])
        
        A = 1
        B = -2*(g**2)*(T + np.dot((initial_pt + ref_pt - camera_pt), beta))
        C = (g**2)*(T**2 - (norm(initial_pt + ref_pt - camera_pt))**2)
        
        D = B**2 - 4*A*C
        t = (-B-math.sqrt(D))/(2*A)
        
        final_pt = initial_pt + t*beta
        points.co.x = final_pt[0]
        points.co.y = final_pt[1]
        points.co.z = final_pt[2]
        
        centroid += np.array(final_pt)
        n+=1
        
    centroid = centroid/n + ref_pt - camera_pt    
    
    return new_mesh, centroid

'''Main Program'''

c = 299792458

dt = datetime.datetime.now()

beta = np.array([0.8,-0.56,0])
velocity = c*beta

b = norm(beta)
g = 1/(math.sqrt(1-b**2))                                   #Defining velocity and other relativistic parameters

fps = 30
dT = 1/(1*fps)                                              #Time Step for each frame

ob = bpy.data.objects["MyObject"]
obj_mesh = bmesh.new()
obj_mesh.from_mesh(ob.data)                                 #Extracting Mesh Data from Object

ref_pt = np.array([ob.location[0], ob.location[1], ob.location[2]])
camera_pt = np.array(bpy.data.objects["Camera"].location)
camera_axis = np.array([0,1,0])
fov = bpy.data.objects['Camera'].data.angle                 #Propertis of Camera

ob_lt_mesh = Lorentz_Contract(obj_mesh)                     #Creating Lorentz-Contracted Mesh

bpy.data.objects['MyObject'].select_set(True)
bpy.context.scene.render.fps = fps
bpy.data.objects['Camera'].data.clip_end = 10000            #Some settings related to animation rendering
bpy.data.window_managers["WinMan"].animall_properties.key_selected = False
bpy.data.window_managers["WinMan"].animall_properties.key_points = True
bpy.context.scene.render.filepath = "E:\\Project Work\\Terrel-Penrose Effect\\Simulation\\Videos\\Terrell_" + str(dt.year) + str(dt.month) + str(dt.day) + str(dt.hour) + str(dt.minute) + str(dt.second)

file_name = 'Data_' + str(dt.year) + str(dt.month) + str(dt.day) + str(dt.hour) + str(dt.minute) + str(dt.second) + '.csv' 
file = open(file_name, 'w', newline='')                     #Creating File for storing positin data for object
writer = csv.writer(file)
writer.writerow(list(beta))
writer.writerow(list(ref_pt))

counter = 0
frame = 0
while True:                                                 #Loop for generating keyframes
    output = Optical_Distort(ob_lt_mesh, counter*dT)        #Generating Optically-Distorted Mesh
    ob_od_mesh = output[0]
    img_centroid = output[1]
    obj_loc = img_centroid + camera_pt
    
    if counter == 0:
        data_ref_pt = tuple(obj_loc)
        
    angle = math.acos(np.dot(img_centroid, camera_axis)/norm(img_centroid)) 
    
    if (angle - 0.087 > fov/2):                             #Calculating angle and checking if object is within Field of View (buffer of approx. 5 deg)
        if frame > 0:
            break
        pass
    else:
        bpy.data.scenes["Scene"].frame_set(frame)           #Setting the frame
        
        initial_cursor = np.array([bpy.context.scene.cursor.location[0],
        bpy.context.scene.cursor.location[1],
        bpy.context.scene.cursor.location[2]])      
        bpy.context.scene.cursor.location = ref_pt  
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')     #Setting Origin of object to reference point
        bpy.context.scene.cursor.location = initial_cursor
        
        ob_od_mesh.to_mesh(ob.data)                         #Updating Mesh Data to the Object
        
        initial_cursor = np.array([bpy.context.scene.cursor.location[0],
        bpy.context.scene.cursor.location[1],
        bpy.context.scene.cursor.location[2]])
        bpy.context.scene.cursor.location = obj_loc
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')     #Updating Origin of Object to Centroid 
        bpy.context.scene.cursor.location = initial_cursor
        
        bpy.ops.anim.insert_keyframe_animall()              #Inserting Keyframes
        ob.keyframe_insert(data_path="location", frame=frame)    
        
        frame+=1

    counter += 1
    data = [counter*(dT/c)*(10**9), frame, angle, obj_loc[0], obj_loc[1], obj_loc[2], norm(obj_loc - np.array(data_ref_pt))] 
    writer.writerow(data)
    print(frame, counter*(dT/c)*(10**9), angle, obj_loc)     #Logging Position of Object with frame and corresponding time

bpy.context.scene.frame_end = frame
bpy.context.scene.cursor.location = [0,0,0]
file.close()
command_1 = "Plot_Distance.py " + str(file_name)
command_2 = "Plot_Velocity.py " + str(file_name)
os.system(command_1)
os.system(command_2)
