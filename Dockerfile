# Use a newer Ubuntu base image that has GLIBC 2.38+
FROM ubuntu:24.04

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv

WORKDIR /app
COPY . /app

# Setup virtual environment and install requirements
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Run Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]