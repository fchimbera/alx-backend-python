# Dockerfile for a Django Messaging Application
# --- Dockerfile Content ---
# Create a file named 'Dockerfile' in the root of your project.

# Use an official Python runtime as a base image.
FROM python:3.12

# Set the working directory inside the container.
WORKDIR /app

# Copy the requirements file into the container.
COPY requirements.txt .

# Install the Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django app code into the container's working directory.
COPY . .

# Expose the port that the Django application will run on.
# The default Django development server port is 8000.
EXPOSE 8000

# Set the command to run the application. This command starts the Django development server.
# It uses 0.0.0.0 as the host to make the server accessible from outside the container.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
