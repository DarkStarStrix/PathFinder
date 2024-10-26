# app.py
from flask import Flask, render_template, jsonify, Response
import pygame
import io
import base64
from A_Pathfinder import Maze
import threading
import queue
import time

app = Flask (__name__)

# Queue for frame updates
frame_queue = queue.Queue (maxsize=30)


class WebMaze (Maze):
    def draw(self, surface):
        super ().draw (surface)
        # Convert pygame surface to base64 image
        image_data = pygame.image.tostring (surface, 'RGB')
        return image_data


def generate_frames():
    pygame.init ()
    surface = pygame.Surface ((800, 800))
    maze = WebMaze ()
    maze.generate_maze_parallel (surface)
    maze.bidirectional_a_star (surface)
    pygame.quit ()


@app.route ('/')
def index():
    return render_template ('index.html')


@app.route ('/start')
def start_maze():
    threading.Thread (target=generate_frames).start ()
    return jsonify ({'status': 'started'})


@app.route ('/stream')
def stream():
    def generate():
        while True:
            try:
                frame = frame_queue.get (timeout=1.0)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except queue.Empty:
                continue

    return Response (generate (),
                     mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run (host='0.0.0.0', port=5000)
