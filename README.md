# Displays Singapore weather

Personal project to learn about http requests using Flask, caching with Redis to reduce API calls from an external site and frontend languages, html and css.

<img width="750" alt="weather app" src="https://github.com/user-attachments/assets/99f92131-dad9-4b2d-a751-fdff2f650f41" />

## Starting the app
1. git clone this repo: ```git@github.com:BowlOfFruits/weather_app.git```
2. Make sure docker is installed. If not, refer to this link https://www.docker.com/get-started/
3. Open your console, and type in the following command: ```docker compose up```
4. Wait for things to install
5. Go into your browser and enter ```localhost:5000```
6. Enjoy!
   

## File structure
```
├── backend
|   ├── app.py
|   ├── utils.py
|   ├── weather_request.py
|   └── classes.py
├── frontend
│   ├── static
|   |   ├── cloud.png
|   |   ├── rain.png
|   |   ├── sun.png
|   |   ├── windypng
|   |   └── weather_style.css
│   └── templates
|   |   └── weather_ui.html
├── Dockerfile
├── compose.yaml
├── README.md
├── .dockerignore
└── .gitignore
```
