#! /bin/bash

echo "Eliminando los containers"
docker-compose down

echo "Creando los nuevos containers"
docker-compose up --build
