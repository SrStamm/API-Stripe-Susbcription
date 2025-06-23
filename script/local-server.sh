#! /bin/bash

echo "Activando Base de datos"
docker start stripe-db

echo "Activando servidor"
uvicorn main:app --reload

echo "Desactivado Base de datos"
docker stop stripe-db
