# Use an official Python runtime as the base image
FROM python:3.7.15-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /usr/src/app

# create log files
RUN mkdir /usr/src/app/logs

# Install the MongoDB client tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        mongo-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first
COPY requirements.txt ./

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the application code
COPY . .

EXPOSE 7000

# Run the migrations (if needed for MongoDB)
# RUN python manage.py makemigrations
# RUN python manage.py migrate

CMD ["python", "manage.py", "runserver", "0.0.0.0:7000"]
