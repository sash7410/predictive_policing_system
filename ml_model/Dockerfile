# Use the official Python image
FROM python:3.9-bullseye

# Set the working directory
WORKDIR /app

# Install Java for PySpark
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Find and set JAVA_HOME dynamically
RUN echo "JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))" >> /etc/environment \
    && . /etc/environment

# Set PATH to include Java
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the ML model files and API script
COPY ml_model/serve_model.py .
COPY ml_model/crime_prediction_model ./crime_prediction_model


CMD ["python", "start_model.py"]