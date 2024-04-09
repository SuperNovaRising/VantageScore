# Summary
This is a self-contained codebase which provides signup, login, authentication, reauthentication functions, DOCKER script to build image and Kubernetes configuration to spin up a cluster locally

This authentication services uses the postgres database `users` to store the username, password of the users

# Build and test FastAPI Server
In case you need to install dependencies later, use `venv` to isolate the working environment from other parts of your computer
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Start/Restart FastAPI Server
```
cd src/auth
uvicorn auth:app --reload
```

## API documentation
Refer to Swagger Docs at `http://127.0.0.1:8000/docs`

# Unit Test
## Prerequisite
You may need to install `pytest`, `requests`, `httpx` in advance
## Run unit test
```
cd src/auth
pytest test_auth.py
```

# Build and push Docker image
## Prerequisites
Please install `Docker `, `minikube`, `k9s` in advance

To ensure minikube's Docker configuration be consistent with the Docker configuration used to build the image, run the command to setup minikube's Docker configuration

```
eval $(minikube docker-env)
```

## Build and push Docker image
You may need to log in to the registry and tag the image accordingly before push
```
docker build -t auth-app .
docker push auth-app:latest
```

## Test Docker container locally
```
docker run -d --name auth-app-container -p 90:80 auth-app
```

You can view the Swagger doc at `http://localhost:90/docs`

# Spin up Kubernetes cluster locally
If you have not, please start minikube
```
minikube start
```
## Deploy to Kubernetes
```
kubectl apply -f auth-deployment.yaml
```

## Expose the application to port 80
```
kubectl expose deployment auth-app --type=NodePort --port=80
```

## Get URL to access the application
```
minikube service auth-app --url
```

The command will return a url like: `http://127.0.0.1:61186`

As a validation, see Swagger doc at `http://127.0.0.1:61186/docs`

# Integration test
## Postman
We could leverage Postman for manual test/exploration and automated integration test

You may need to install [Postman desktop agent](https://www.postman.com/downloads/postman-agent/) to access local resources

### Import Open API specification to Postman
Import the json string in [FastAPI.postman_collection](Auth.postman_collection.json) to postman. You may need to adjust the environment variable `baseUrl` to `127.0.0.1:61186`

Now you can manually test each API.


## Clean up
Terminate the console running the service
```
kubectl delete  deployments auth-app
kubectl delete svc auth-app
```
