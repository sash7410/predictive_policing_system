# Use the official Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the ML model files and API script
COPY . .

# Expose the Flask API port
EXPOSE 5000

# Run the Flask API
CMD ["python", "serve_model.py"]
