import tkinter as tk
#from mttkinter import mtTkinter as tk
import numpy as np
import multiprocessing
from queue import Queue
import math
import time

CANVAS_WIDTH  = 1920*2#960
CANVAS_HEIGHT = 1080*2#540
PIXEL_COUNT   = CANVAS_WIDTH * CANVAS_HEIGHT
FULLSCREEN    = True
VERSION       = "V1.2.0"
BACKGROUND_COLOR = (255, 255, 255)

class Camera:
	def __init__(self, origin, frame_width, frame_height, frame_distance):
		self.origin = origin
		self.frame_width  = frame_width
		self.frame_height = frame_height
		self.frame_distance = frame_distance

class RenderObject:
	def __init__(self, position, scale):
		self.position = position
		self.scale = scale

class Sphere(RenderObject):
	"""
	Scaled unit Sphere
	"""
	def __init__(self, centroid, radius, color):
		super().__init__(centroid, radius)
		self.color = color
	
	def __getattr__(self, attr):
		if attr == "centroid":
			return self.position
		elif attr == "radius":
			return self.scale

def mainloop():
	window = tk.Tk()
	window.geometry(f"{CANVAS_WIDTH//2}x{CANVAS_HEIGHT//2}")
	window.attributes("-fullscreen", FULLSCREEN)
	window.title(f"The Quadrantal Rendering Engine - {VERSION}")
	canvas = tk.Canvas(window, bd=0, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
	
	camera = Camera((-1, 0, 0), 16/9, 1, 1)
	render_objects = [
						Sphere((0, 1, 4), 0.5, (0, 255, 255)),
						Sphere((0, 0.5, 4), 0.5, (255, 255, 0))
					 ]
	canvas.create_rectangle(10, 10, 50, 50)
	canvas.pack()
	window.update()
	while True:
		p=render_objects[1].position; render_objects[1].position=(p[0], p[1]+0.1, p[2])
		screen = render(canvas, camera, render_objects)
		canvas.pack()
		window.update()

def canvas_to_viewport(camera, x, y):
	return (x*camera.frame_width/CANVAS_WIDTH, y*camera.frame_height/CANVAS_HEIGHT, camera.frame_distance)
	
def trace_ray(camera, render_objects, D, t_min, t_max):
	closest_t = math.inf
	closest_sphere = None
	for sphere in render_objects:
		t1, t2 = intersect_ray_sphere(camera, D, sphere)
		if t1 > t_min and t1 < t_max and t1 < closest_t:
			closest_t = t1
			closest_sphere = sphere
		if t2 > t_min and t2 < t_max and t2 < closest_t:
			closest_t = t2
			closest_sphere = sphere
	if closest_sphere is None:
		return BACKGROUND_COLOR
	return closest_sphere.color

def intersect_ray_sphere(camera, D, sphere):
	r = sphere.radius
	CO = np.subtract(camera.origin, sphere.centroid)
	a = np.dot(D, D)
	b = 2*np.dot(CO, D)
	c = np.dot(CO, CO) - r*r
	discriminant = b*b - 4*a*c
	if discriminant < 0:
		return math.inf, math.inf
	t1 = (-b + math.sqrt(discriminant)) / (2*a)
	t2 = (-b - math.sqrt(discriminant)) / (2*a)
	return t1, t2

gcamera = grender_objects = None

def get_color(p):
	x, y = p[0], p[1]
	frame_point = canvas_to_viewport(gcamera, x, y)
	color = trace_ray(gcamera, grender_objects, frame_point, 1, math.inf)
	return (x, y, f"#{hex(color[0])[2:].zfill(2)}{hex(color[1])[2:].zfill(2)}{hex(color[2])[2:].zfill(2)}")

def render(canvas, camera, render_objects):
	stime = time.perf_counter()
	grid = np.ndindex((CANVAS_WIDTH//2,CANVAS_HEIGHT//2))
	global gcamera, grender_objects
	gcamera = camera
	grender_objects = render_objects
	with  multiprocessing.Pool() as pool:
		colors = pool.map(get_color, grid)
	ctime = time.perf_counter()
	print("Processing:", ctime-stime)
	for x, y, color in colors:
		canvas.create_rectangle(x, y, x, y, outline="", fill=color)
	print("Displaying:", time.perf_counter()-ctime)
if __name__ == "__main__":
	mainloop()
