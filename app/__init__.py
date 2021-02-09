from flask import Flask
import config
from flasgger import Swagger, swag_from

template = {
  "swagger": "2.0",
  "info": {
    "title": "Flask Restful Swagger Demo",
    "description": "A Demof for the Flask-Restful Swagger Demo",
    "version": "0.1.1",
    "contact": {
      "name": "Kanoki",
      "url": "https://Kanoki.org",
    }
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
    "specs_route": "/swagger/"
}
swagger = Swagger(app, template= template)
app.config.from_object(config.Config)

from app import views

