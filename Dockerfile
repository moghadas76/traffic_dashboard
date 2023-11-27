# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory to /app
WORKDIR /dashboard

# Copy the current directory contents into the container at /app
COPY . /dashboard

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -e .

# Make port 8050 available to the world outside this container
EXPOSE 8050

# Define environment variable
WORKDIR /dashboard/src/dashboard
# Run the cleaner.sh script in the background
CMD ["sh", "-c", "./scripts/cleaner.sh & python app.py"]
