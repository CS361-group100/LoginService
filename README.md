# CS361---LoginService
This is the login microservice implementation for microservice 3 of group 100 of CS361.
## Description
This microservice is responsible for user login, allowing users to register 
and log in securely. It implements features like rate limiting and account lockouts to enhance security. Users can create accounts, log in, and are subject to restrictions after multiple failed login attempts.

## Communication Contract

### Endpoints

#### 1. User Registration
- **URL**: `/auth/register`
- **Method**: `POST`
- **Request Body**: 
```json
{
    "username": "user\_example",
    "password": "SecurePassword123"
}
```

- **Response**:
  - **201 Created** on successful registration.
  - **409 Conflict** if the username is already taken.
  - **400 Bad Request** if the password does not meet length constraints.

#### Example Request (Registration)
```bash

curl -X POST http://localhost:5000/auth/register -H "Content-Type: application/json" -d '{"username": "user1", "password": "StrongPassword123"}'
```
#### Example Response (Registration)
```json
{
  "message": "User created. Please sign in."
}
   ````

#### 2. User Login
- **URL**: `/auth/login`
- **Method**: `POST`
- **Request Body**: 
````json
{
    "username": "user\_example",
    "password": "SecurePassword123"
}
````

- **Response**: 
    - **200 OK** on successful login, with user details and an access token.
    - **401 Unauthorized** if the credentials are invalid.
    - **403 Forbidden** if the user is blocked due to too many failed attempts.

#### Example Request (Login)
````bash
curl -X POST http://localhost:5000/auth/login -H "Content-Type: application/json" -d '{"username": "user1", "password": "StrongPassword123"}'
````

#### Example Response (Login)

````json
{
    "user": {
        "userId": 1,
        "username": "user1",
        "displayName": "User"
    },
    "accessToken": "your\_jwt\_token\_here"
}
````
#### UML Sequence Diagram

Below is the UML sequence diagram illustrating the flow of requesting and receiving data from the microservice:

````plaintext
Copy Code
+----------------+                   +-------------------+
|     Client     |                   | User Auth Service  |
+----------------+                   +-------------------+
        |                                     |
        | 1. Send Registration Request        |
        |------------------------------------>|
        |                                     |
        | 2. Process Registration             |
        |                                     |
        | 3. Respond with Success or Error    |
        |<------------------------------------|
        |                                     |
        | 4. Send Login Request               |
        |------------------------------------>|
        |                                     |
        | 5. Process Login                    |
        |                                     |
        | 6. Respond with User Data or Error  |
        |<------------------------------------|
        |                                     |
````

#### Description of the Sequence Diagram
1. The Client sends a registration request to the Login Microservice. 
2. The service processes the registration, either adding the new user to 
   the database or returning an error if the username is taken, or the 
   password is not long enough. 
3. The service responds to the client with either a success message or an error. 
4. The client then sends a login request to the service. 
5. The service processes the login attempt, checking the provided credentials. 
6. The service responds with user data and an access token upon successful login, or an error if the login fails.

#### Conclusion

This microservice enables users to register and log in securely while implementing measures to prevent unauthorized access and abuse. Please adhere to the communication contract defined here to ensure smooth integration with other services.