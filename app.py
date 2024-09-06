from flask import Flask, render_template, Response, request, jsonify
from flask_socketio import SocketIO
import cv2
from object_detection import ObjectDetector
from llm_summary import summarize_events
import time
from collections import deque, Counter
import logging
from datetime import datetime, timedelta
import re

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize video capture and object detector
cap = cv2.VideoCapture(0)
detector = ObjectDetector()

# Event log
event_log = deque(maxlen=1000)  # Store last 1000 events

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sampling frequency
sampling_frequency = 60  # Default to 60 seconds
last_update_time = time.time()

# Temporary storage for objects detected within the current sampling window
current_window_objects = set()

# Total object counts since the application started
total_object_counts = Counter()

def generate_frames():
    global last_update_time, current_window_objects, total_object_counts
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Perform object detection
            objects = detector.detect_objects(frame)

            # Add detected objects to the current window set and update total counts
            for obj in objects:
                label = obj[0]
                current_window_objects.add(label)
                total_object_counts[label] += 1

            # Check if it's time to update the frontend
            current_time = time.time()
            if current_time - last_update_time >= sampling_frequency:
                update_frontend()
                last_update_time = current_time

            # Draw bounding boxes on the frame
            for obj in objects:
                label, confidence, (x, y, w, h) = obj
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"{label}: {confidence:.2f}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # Encode the frame for streaming
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def update_frontend():
    global current_window_objects, total_object_counts
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create an event with unique objects detected in this window
    event = {
        'timestamp': timestamp,
        'objects': list(current_window_objects)
    }
    event_log.append(event)

    # Format and emit log entry
    log_entry = f"Objects detected between {timestamp} and {sampling_frequency} seconds prior: {', '.join(event['objects'])}"
    socketio.emit('log_update', {'log_entry': log_entry})

    logger.info(f"Event logged: {event}")

    # Create a dictionary of object counts for the current window
    current_window_counts = Counter(current_window_objects)

    # Prepare time series data and object counts
    time_series_data = [{'timestamp': timestamp, 'object_counts': dict(current_window_counts)}]

    # Emit update to frontend
    socketio.emit('update', {
        'time_series_data': time_series_data,
        'object_counts': dict(current_window_counts),
        'total_object_counts': dict(total_object_counts)
    })

    logger.info(f"Frontend updated with {len(current_window_objects)} unique objects")

    # Clear the current window objects for the next sampling period
    current_window_objects.clear()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/query_events', methods=['POST'])
def query_events():
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({'summary': "No query provided. Please ask a question about events."})

    logger.info(f"Received query: {query}")

    # Parse the query to determine the time range
    time_range = parse_time_query(query)
    
    if time_range is None:
        return jsonify({'summary': "I'm sorry, I couldn't understand the time range in your query. Please try again with a clearer time specification, such as 'What happened in the last 10 minutes?' or 'What happened between 14:00 and 15:00?'"})

    start_time, end_time = time_range
    
    logger.info(f"Querying events between {start_time} and {end_time}")

    # Filter events within the specified time range
    filtered_events = [event for event in event_log if start_time <= datetime.strptime(event['timestamp'], "%Y-%m-%d %H:%M:%S") <= end_time]
    
    logger.info(f"Found {len(filtered_events)} events in the specified time range")

    # Generate summary using LLM
    summary = summarize_events(filtered_events, start_time.strftime("%Y-%m-%d %H:%M:%S"), end_time.strftime("%Y-%m-%d %H:%M:%S"))
    
    logger.info(f"Generated summary: {summary}")

    return jsonify({'summary': summary})

def parse_time_query(query):
    now = datetime.now()
    
    # Check for "last X seconds/minutes/hours"
    last_time_match = re.search(r'last (\d+) (second|minute|hour)s?', query, re.IGNORECASE)
    if last_time_match:
        amount = int(last_time_match.group(1))
        unit = last_time_match.group(2).lower()
        if unit == 'second':
            delta = timedelta(seconds=amount)
        elif unit == 'minute':
            delta = timedelta(minutes=amount)
        else:  # hour
            delta = timedelta(hours=amount)
        end_time = now
        start_time = end_time - delta
        return start_time, end_time

    # Check for "between HH:MM and HH:MM"
    between_time_match = re.search(r'between (\d{2}:\d{2}) and (\d{2}:\d{2})', query)
    if between_time_match:
        start_time_str = between_time_match.group(1)
        end_time_str = between_time_match.group(2)
        start_time = datetime.strptime(f"{now.date()} {start_time_str}", "%Y-%m-%d %H:%M")
        end_time = datetime.strptime(f"{now.date()} {end_time_str}", "%Y-%m-%d %H:%M")
        if end_time < start_time:
            end_time += timedelta(days=1)  # Assume it's for the next day
        return start_time, end_time

    # If no recognized time format, return None
    return None

@app.route('/set_interval', methods=['POST'])
def set_interval():
    global sampling_frequency, last_update_time, current_window_objects
    sampling_frequency = int(request.form['interval'])
    last_update_time = time.time()  # Reset the timer when interval changes
    current_window_objects.clear()  # Clear the current window when interval changes
    logger.info(f"Sampling frequency updated to {sampling_frequency} seconds")
    return '', 204

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8080)