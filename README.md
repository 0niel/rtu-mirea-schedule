# Schedule-RTU

Forked from https://github.com/RTUITLab/Schedule-RTU-API

Service for getting jsons with a schedule for a given group of RTU MIREA

# Build service from Docker image
Requirements:
* Docker

## Run container:

Clone or download this repo and build container 
* ```docker build -t schedule-rtu:latest .```

Run container
* ```docker run -it -p 5000:5000 schedule-rtu:latest```

App running on ```http://0.0.0.0:5000/```

You can find api on ```http://localhost:5000/redoc ```

## Deploy

Run next command to generate swarm stack file
```bash
# bash
docker-compose -f docker-compose.yml -f docker-compose.production.yml config | sed "s/[0-9]\+\.[0-9]\+$/'\0'/g" >| stack.yml
```
