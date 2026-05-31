# Postman Collection

## Importing the Collection

1. Import `CortexFlow.postman_collection.json`
2. Import `CortexFlow.postman_environment.json`
3. Configure the environment variables according to your setup

## Environment Variables

| Variable       | Description                                      |
| -------------- | ------------------------------------------------ |
| `token`        | JWT access token used for authenticated requests |
| `base_url`     | Base URL of the API                              |

## Usage Flow

1. Run the **Login** request.
2. Copy the returned JWT access token.
3. Set the token in the `token` environment variable.
4. Execute the protected endpoints.

## Files

* `CortexFlow.postman_collection.json` — Contains all API endpoints, requests, and test scripts.
* `CortexFlow.postman_environment.json` — Contains environment variables required to run the collection.

## Requirements

* A running instance of the CortexFlow API.
* A valid user account to authenticate and obtain an access token.
