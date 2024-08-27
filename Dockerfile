# Use an official Python runtime as a parent image
FROM python:3.12.2-slim

# Install git and graphviz
RUN apt-get update && apt-get install -y \
    git \
    graphviz \
    build-essential \
    cmake \
    && apt-get clean

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

COPY .env .

# Install any dependencies specified in requirements.txt
#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["sh", "-c", "export $(grep -v '^#' .env | xargs) && uvicorn app.fasthtml_app:app --host 0.0.0.0 --port 8000 --reload"]
