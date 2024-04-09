# Summary
This document describes how to manually test the workflow using Postman. It demonstrates users are granted different level of privilege based on their identities. Unregistered users are blocked from accessing the APIs.

# Setup
Boot up postgres on local kubernetes cluster, refer to [postgres README.md](../src/postgres/README.md)

Boot up AuthService on local kubernetes cluster, refer to [AuthService README.md](../src/auth/README.md). Note the port.

Boot up EmployeeService on Uvicorn, refer to [EmployeeService README.md](../src/employee/README.md). Note the port.

Import the Auth and Employee collections to Postman and create an environment to store `authBaseUrl` and `employeeUrl`

# Predefined configuration
Basic user/password has been configured.
```
 username |                       hashed_password                        
----------+--------------------------------------------------------------
 admin    | $2y$10$Fxi.qVv8Y9jK9ivO1xJN8OyRgK9gZfQNhYWimSnjToK2L0xcY6h/.
 other    | $2y$10$ARSTZKmiD5JXhaae9FolAuy06KJGHupFgjWei4ucW2gUGLbywo1HC
 ```

# Test
For brevity, below shows the `curl` commands. You can easily convert `curl` to more readable format in Postman

## Admin login with predefined password and be able to use all EmployeeService APIs
Log in using admin's username and password and obtain JWT. Copy the JWT for later use.
```
curl --location '127.0.0.1:57610/login/' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--header 'Accept: application/json' \
--data-urlencode 'username=admin' \
--data-urlencode 'password=$2y$10$Fxi.qVv8Y9jK9ivO1xJN8OyRgK9gZfQNhYWimSnjToK2L0xcY6h/.' 
```
Create a new employee
```
curl --location '127.0.0.1:8000/employees/' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcxMjY0MDg2OH0.JeegMruOmBr7rWYHEE6cZm1ib9vG3BYgBRdEgD30wTo' \
--data '{
  "employee_id": "1",
  "employee_name": "John Doe"
}'
```

Get an employee
```
curl --location '127.0.0.1:8000/employees/1' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcxMjY0MDg2OH0.JeegMruOmBr7rWYHEE6cZm1ib9vG3BYgBRdEgD30wTo'
```

Update an employee
```
curl --location --request PUT '127.0.0.1:8000/employees/1' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcxMjY0MDg2OH0.JeegMruOmBr7rWYHEE6cZm1ib9vG3BYgBRdEgD30wTo' \
--data '{
  "employee_id": "1",
  "employee_name": "Mary Jane"
}'
```

Delete an employee
```
curl --location --request DELETE '127.0.0.1:8000/employees/2' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcxMjY0MDg2OH0.JeegMruOmBr7rWYHEE6cZm1ib9vG3BYgBRdEgD30wTo'
```

## Existing non-admin user logs in and can only use GET API
Log in using `other`'s username and password and obtain JWT. Copy the JWT for later use.
```
curl --location '127.0.0.1:57610/login/' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--header 'Accept: application/json' \
--data-urlencode 'username=other' \
--data-urlencode 'password=$2y$10$ARSTZKmiD5JXhaae9FolAuy06KJGHupFgjWei4ucW2gUGLbywo1HC'
```

Create an employee
```
curl --location '127.0.0.1:8000/employees/' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJvdGhlciIsImV4cCI6MTcxMjY0MTI2Mn0.Z_wYvjXWVE8CHiBckz8vf1JNt6zjvsBwULhbVNSRPEg' \
--data '{
  "employee_id": "1",
  "employee_name": "John Doe"
}'
```
The user got 400 error: 
```
{
    "detail": "The user doesn't have enough privileges"
}
```

Get an employee
```
curl --location '127.0.0.1:8000/employees/1' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJvdGhlciIsImV4cCI6MTcxMjY0MTI2Mn0.Z_wYvjXWVE8CHiBckz8vf1JNt6zjvsBwULhbVNSRPEg'
```
The user got 200 response:
```
{
    "employee_id": 1,
    "employee_name": "Mary Jane"
}
```

Update an employee
```
curl --location --request PUT '127.0.0.1:8000/employees/1' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJvdGhlciIsImV4cCI6MTcxMjY0MTI2Mn0.Z_wYvjXWVE8CHiBckz8vf1JNt6zjvsBwULhbVNSRPEg' \
--data '{
  "employee_id": "1",
  "employee_name": "Mary Jane"
}'
```
The user got 400 error:
```
{
    "detail": "The user doesn't have enough privileges"
}
```

Delete an employee
```
curl --location --request DELETE '127.0.0.1:8000/employees/2' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJvdGhlciIsImV4cCI6MTcxMjY0MTI2Mn0.Z_wYvjXWVE8CHiBckz8vf1JNt6zjvsBwULhbVNSRPEg'
```
The user got 400 error:
```
{
    "detail": "The user doesn't have enough privileges"
}
```

## Unregistered user trying to get an employee without JWT
```
curl --location '127.0.0.1:8000/employees/1' \
--header 'Accept: application/json'
```
Thee user got 401 error:
```
{
    "detail": "Not authenticated"
}
```

## Register a new user
Register a new user `integration_test`. Assume the password is `password`. Use [bcrypt](https://bcrypt.online/?plain_text=nosecret&cost_factor=10) to encrypt the password. The encrypted password is `$2y$10$jFeTDMAgZmXnanA5qmja9uSBKaSIcA3OtELkO2WqODuwDUOyXQXQm`

Register the user
```
curl --location '127.0.0.1:57610/signup/' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--data '{
  "username": "integration_test",
  "hashed_password": "$2y$10$jFeTDMAgZmXnanA5qmja9uSBKaSIcA3OtELkO2WqODuwDUOyXQXQm"
}'
```
Response:
```
{
    "username": "integration_test",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpbnRlZ3JhdGlvbl90ZXN0IiwiZXhwIjoxNzEyNjQyODE5fQ.K4h32zLmfAf7uRkBE4Lc4PmUG8aj9YpFTQVWYJT0CVY"
}
```
Use the JWT to access Get Employee API
```
curl --location '127.0.0.1:8000/employees/1' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpbnRlZ3JhdGlvbl90ZXN0IiwiZXhwIjoxNzEyNjQyODE5fQ.K4h32zLmfAf7uRkBE4Lc4PmUG8aj9YpFTQVWYJT0CVY'
```
