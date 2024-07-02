# Use the official Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Copy the rest of the application code into the container
COPY . .

# Set the entrypoint
ENTRYPOINT ["python", "media_organizer.py"]