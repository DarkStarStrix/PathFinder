# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pygame \
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variable for Pygame to run headless
ENV SDL_VIDEODRIVER=dummy
ENV PYTHONUNBUFFERED=1

# Expose port (if your application uses a specific port)
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
