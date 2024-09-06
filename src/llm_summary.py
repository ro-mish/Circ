import requests
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv(".env")

# Get API key from environment variable
API_KEY = os.getenv('OPENAI_API_KEY')

def generate_llm_summary(objects):
    """
    Generate a summary of detected objects using an LLM.
    
    :param objects: List of detected object labels
    :return: String containing the LLM-generated summary
    """
    if not objects:
        return "No objects detected."

    objects_str = ", ".join(set(objects))
    prompt = f"Summarize the following objects detected around a home: {objects_str}"
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "model": "gpt-3.5-turbo",  # Specify the model
                "messages": [{"role": "user", "content": prompt}],  # Corrected payload
                "max_tokens": 100
            }
        )
        response.raise_for_status()
        
        summary = response.json()["choices"][0]["message"]["content"].strip()  # Updated key access
        return summary
    except requests.exceptions.RequestException as e:
        print(f"Error calling OpenAI API: {e}")
        return "Error generating summary."

# Add a new function to handle frame summarization
def summarize_frame(frame, objects):
    """
    Generate a summary of a frame based on detected objects.
    
    :param frame: The video frame (numpy array)
    :param objects: List of detected object labels
    :return: String containing the LLM-generated summary
    """
    # Convert frame to base64 for potential future use with image-based models
    # For now, we'll just use the object labels
    summary = generate_llm_summary(objects)
    return summary

def summarize_batch(object_batch, sampling_frequency):
    """
    Generate a summary of detected objects using an LLM for a batch of detections.
    
    :param object_batch: Dictionary of object labels and their counts
    :param sampling_frequency: The time interval in seconds for this batch
    :return: String containing the LLM-generated summary
    """
    if not object_batch:
        return f"No objects detected in the last {sampling_frequency} seconds."

    # Create a string representation of object counts
    objects_str = ", ".join(f"{count} {obj}" for obj, count in object_batch.items())
    prompt = f"Summarize the following objects detected around a home in the last {sampling_frequency} seconds: {objects_str}. Format the summary as 'Within the last {sampling_frequency} seconds, there were [count] detections of [type]' for each object type."
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200
            })
        )
        response.raise_for_status()
        
        response_data = response.json()
        if 'choices' in response_data and len(response_data['choices']) > 0:
            summary = response_data['choices'][0]['message']['content'].strip()
            return summary
        else:
            print(f"Unexpected API response: {response_data}")
            return "Error: Unexpected API response format."
    except requests.exceptions.RequestException as e:
        print(f"Error calling OpenAI API: {e}")
        return f"Error generating summary for the last {sampling_frequency} seconds."
    except json.JSONDecodeError as e:
        print(f"Error decoding API response: {e}")
        return "Error: Unable to decode API response."
    except KeyError as e:
        print(f"Error accessing API response data: {e}")
        return "Error: Unexpected API response structure."

# For testing purposes
if __name__ == "__main__":
    test_batch = {"person": 2, "car": 1, "dog": 3}
    print(summarize_batch(test_batch, 60))

def summarize_events(events, start_time, end_time):
    """
    Generate a summary of events within a specified time range using an LLM.
    
    :param events: List of event dictionaries
    :param start_time: Start time of the query range
    :param end_time: End time of the query range
    :return: String containing the LLM-generated summary
    """
    if not events:
        return f"No events detected between {start_time} and {end_time}."

    # Create a string representation of events
    events_str = "\n".join([f"{event['timestamp']}: {', '.join(event['objects'])}" for event in events])
    prompt = f"Summarize the following events detected between {start_time} and {end_time}:\n\n{events_str}\n\nProvide a natural language summary of what happened during this time period."
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200
            })
        )
        response.raise_for_status()
        
        response_data = response.json()
        if 'choices' in response_data and len(response_data['choices']) > 0:
            summary = response_data['choices'][0]['message']['content'].strip()
            return summary
        else:
            print(f"Unexpected API response: {response_data}")
            return "Error: Unexpected API response format."
    except requests.exceptions.RequestException as e:
        print(f"Error calling OpenAI API: {e}")
        return f"Error generating summary for events between {start_time} and {end_time}."
    except json.JSONDecodeError as e:
        print(f"Error decoding API response: {e}")
        return "Error: Unable to decode API response."
    except KeyError as e:
        print(f"Error accessing API response data: {e}")
        return "Error: Unexpected API response structure."