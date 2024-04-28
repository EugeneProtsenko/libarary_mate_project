# Use an official Python runtime as a parent image
FROM python:3.12.1-slim
LABEL maintainer="guitaaarpro@gamil.com"

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# Create media directory
RUN mkdir -p /vol/web/media

# Create a user
RUN adduser --disabled-password --no-create-home library_user

# Change file ownership and permissions
RUN chown -R library_user:library_user /vol/
RUN chmod -R 755 /vol/web/

# Switch to the new user
USER library_user
