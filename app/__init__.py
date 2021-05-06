from flask import Flask
import config
from flasgger import Swagger, swag_from

template = {
  "swagger": "2.0",
  "info": {
    "title": "SCHEDULE-RTU",
    "description": "API for getting schedule for RTU MIREA",
    "version": "1.0.0",
    # "contact": {
    #   "name": "Kanoki",
    #   "url": "https://Kanoki.org",
    # }
  },
  "securityDefinitions": {
    "Bearer": {
      "type": "apiKey",
      "name": "Authorization",
      "in": "header",
      "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
    }
  },
  "security": [
    {
      "Bearer": [ ]
    }
  ]

}

app = Flask(__name__)

app.config['SWAGGER'] = {
    'title': 'My API',
    'uiversion': 3,
    "specs_route": "/api/schedule/swagger/"
}
swagger = Swagger(app, template= template)
app.config.from_object(config.Config)


from app import views

