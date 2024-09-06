.PHONY: setup download_yolo create_env install_deps create_env_file run

setup: download_yolo create_env install_deps create_env_file
	@echo "Setup complete! You can now run the application with 'make run'"

download_yolo:
	@echo "Downloading YOLO files..."
	@curl -O https://pjreddie.com/media/files/yolov3.weights
	@curl -O https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg
	@curl -O https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names

create_env:
	@echo "Creating virtual environment..."
	@python3 -m venv venv
	@echo "Activating virtual environment..."
	@. venv/bin/activate

install_deps: create_env
	@echo "Installing dependencies..."
	@pip install -r requirements.txt

create_env_file:
	@echo "Creating .env file..."
	@if [ ! -f .env ]; then \
		read -p "Enter your OpenAI API key: " api_key; \
		echo "OPENAI_API_KEY=$$api_key" > .env; \
		echo ".env file created with API key."; \
	else \
		echo ".env file already exists. Skipping."; \
	fi

run:
	@echo "Running the application..."
	@. venv/bin/activate && python src/app.py

clean:
	@echo "Cleaning up..."
	@rm -rf venv
	@rm -f yolov3.weights yolov3.cfg coco.names
	@rm -f .env