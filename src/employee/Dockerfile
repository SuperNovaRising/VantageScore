# Use an official Python runtime as a parent image
FROM python:3.10-slim-bullseye

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

RUN pip install --upgrade pip
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
# Setting python path to allow employee module to import auth module
ENV PYTHONPATH="${PYTHONPATH}:/app/src"

RUN pip install uvicorn

# Run app.py when the container launches
CMD ["uvicorn", "employee:app", "--host", "0.0.0.0", "--port", "80"]
