# Schedule-RTU
Service for getting jsons with a schedule for a given group of RTU MIREA

# Build service from Docker image
Requirements:
* Docker

## Test local container:

This is a development server. Do not use it in a production deployment.

Clone or download this repo and build container 
* ```docker build -t schedule-rtu:latest .```

Run container
* ```docker run -p 5000:5000 schedule-rtu:latest```

App running on ```http://0.0.0.0:5000/ ```

