# Circ: Home Management, Detection and Event Logging System

This project implements a real-time object detection system with event logging and querying capabilities using Flask, OpenCV, and OpenAI's GPT-3.5 model.

## Prerequisites

- Python 3.7+
- pip (Python package manager)
- make (for using the Makefile)
- Webcam or video input device

## Installation

1. Clone the repository:
   ```
   git clone git@github.com:ro-mish/Circ.git
   cd Circ
   ```

2. Run the setup process using make:
   ```
   make setup
   ```
   This will:
   - Download the required YOLO files
   - Create a virtual environment
   - Install the required packages
   - Prompt you to enter your OpenAI API key and create a .env file

## Usage

1. Run the Flask application:
   ```
   make run
   ```

2. Open a web browser and navigate to `http://localhost:8080`

3. The web interface will display:
   - Live video feed with object detection
   - Time series chart of detected objects
   - Bar chart of total object occurrences
   - Event logs
   - Chat interface for querying events

4. Use the dropdown menu to adjust the sampling frequency for event logging.

5. Use the chat interface to ask questions about events, such as:
   - "What happened in the last 5 minutes?"
   - "What happened between 14:00 and 15:00?"

## Project Structure

- `src/app.py`: Main Flask application
- `src/object_detection.py`: YOLO object detection implementation
- `src/llm_summary.py`: OpenAI GPT-3.5 integration for event summarization
- `src/notification.py`: Placeholder for notification system
- `src/templates/index.html`: Web interface template

## Customization

- To modify the object detection model, update the YOLO configuration in `src/object_detection.py`
- To change the UI appearance, edit the styles in `src/templates/index.html`
- To add new features or modify existing ones, update the relevant Python files and the HTML template

## Troubleshooting

- If you encounter issues with the video feed, ensure your webcam is properly connected and not being used by another application.
- If the OpenAI API calls fail, check your API key in the `.env` file and ensure you have sufficient credits.

## Cleaning Up

To remove all generated files and the virtual environment: delete the whole thing. The app won't save anything. Enjoy :)