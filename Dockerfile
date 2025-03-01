FROM python:3.13-slim

WORKDIR /app

# Copy all files and folders from /weather_app into the container's /app
COPY . .

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Run the app. Include host=0.0.0.0 as we are accessing it from outside the container
CMD ["python3", "-m", "flask", "--app", "./backend/app.py", "run", "--host=0.0.0.0", "--debug"]

