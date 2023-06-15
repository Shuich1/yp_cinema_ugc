FROM python:3.10.9-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONWARNINGS="ignore"

# Install netcat for checking postgres availability
RUN apt-get update && apt-get install -y netcat

# Adjust the path to the requirements.txt
COPY ../usg_sprint_9_research/requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade pip -r /requirements.txt

# Adjust the path to the src directory
COPY ../src /opt/app
WORKDIR /opt/app

# Copy the entrypoint script
COPY ../usg_sprint_9_research/entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Set the entrypoint script as the entrypoint of the container
ENTRYPOINT ["/entrypoint.sh"]
