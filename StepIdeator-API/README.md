# StepIdeator-API

API server for StepIdeator.

## Introduction

### Key Dependencies

- `Python / Conda` : Run `python --version` to check if Python is installed. You can also use Conda to create a Python virtual environment. The development environment uses Python version 3.9.18. Due to compatibility issues with certain dependencies, versions above Python 3.11 are not supported.
- `Flask` : A lightweight backend API service framework.
- `Pymongo` : A Python library for interacting with MongoDB.
- `MongoDB` : A NoSQL database used to store user data and experiment data (including text and images).
- `OpenAI` : A Python library for interacting with OpenAI services.

Additionally, other dependencies are installed via `pip` and `conda`, as specified in the `./environment.yml` file.

### Project Architecture

The project structure is as follows:

``` sh
├── agent
├── app.py
├── apps
├── config.py
├── environment.yml
├── README.md
├── settings
└── uwsgi.ini
```
- App : `app.py` is the entry point of the project. You can configure the application’s port and other settings here.
- Routes: Routes are defined in `./apps/routes.py`. New routes and route collections can easily be added following a similar approach. For more information, refer to Flask’s documentation on blueprints: https://flask.palletsprojects.com/en/3.0.x/blueprints/

- Prompts: Designers can write prompts in `./settings`. Developers can dynamically call these prompts within the program using templates for flexibility and ease of use.
- Logic: The backend’s logic resides in `apps/${app_name}`. Currently, only one app is implemented. If a new app is required, a new folder can be created, and its logic added. Be sure to include the new `APP_ID` in `./config.py`.
- Algorithm Invocation: The modules for algorithm invocation are located in the `agent` directory. Currently, both Stable Diffusion (SD) and GPT are supported. The SD module includes an instance pool that enables load balancing across multiple SD instances, improving generation efficiency (this requires multiple SD instances to be running).
- Configuration File: The configuration file is located in `./config.py`, where you can modify settings such as:
    - APP IDs
    - Stable Diffusion service API paths
    - Azure OpenAI GPT service configurations
    - Database settings

### Data Transfer

Data transfer between the frontend and backend follows standard HTTP request conventions. All requests that modify the database or use generative capabilities should be made using `POST` requests, while all other query-based requests should use `GET` requests.

When sending text data from the frontend to the backend via a `POST` request, the data should be passed in JSON format within the body of the request. The frontend must also include the header `"Content-Type": "application/json"`. Here’s an example of a frontend request:

```javascript
const res = await fetch(`${baseUrl}/paint/start`, {
    method: "POST",
    body: JSON.stringify({
        username
    }),
    headers: {
        "Content-Type": "application/json",
    },
});
```

On the backend, the corresponding route handler retrieves the data from the request body and processes it as follows:

```python
@apps.route('/paint/start', methods=['POST'])
def paintStart():
    try:
        username = request.json.get('username')
        if username == '':
            raise BusinessException(BUSINESS_FAIL, 'User name cannot be empty')
        ... 
```

Note: Currently, all data transfers are handled using JSON format. When transmitting image files, the frontend should convert the image to a BASE64-encoded string and send it as a string to the backend. This method is more suited for scenarios where multiple images need to be transferred.

### Large Model Integration

The system currently integrates two large models: GPT and Stable Diffusion. The code for these models is located in the `agent` directory.

- GPT: Text generation capabilities are provided by GPT-4 from OpenAI, and the project accesses the service through Azure’s API. The system implements a `chat` interface to provide prompts and generate the required text.
- Stable Diffusion (SD): Image generation is powered by SD. To run the project, you must first set up an SD service locally and run SD instances. The project interacts with the SD service using its API. The following functionality has been implemented:
    - `call_sdapi` and `post_sdapi`: These two interfaces correspond to `GET` and `POST` requests for invoking the SD service’s API. Based on these, other specific functions, such as `text2Image`, can be built.
    - `text2Image`: This function is based on `post_sdapi`, invoking SD’s capability to generate images from text.

To support the simultaneous use of multiple SD instances, a SD Instance Pool (SDInstancePool) has been implemented. The code for this pool is located in `agent/sd.py`. The pool is initialized with the SD instances defined in the configuration file. When SD functionality is used, the instance pool automatically assigns an available SD instance to execute the task, and if all instances are busy, it blocks other tasks until an instance becomes available.


## Quick start

1. Set up the environment and install dependencies (if you already have an environment, you can directly install dependencies).
Run the following command:

    ```bash
    conda env create -f environment.yml
    ```

2. Activate the Conda environment:

    ```bash
    conda activate stepideator
    ```

3. Ensure all backend services are running and configured correctly, including:
    - Stable Diffusion
    - Azure GPT service
    - MongoDB service is up and running

4.	Start the project within the Conda environment by running:

    ```bash
    python app.py
    ```

5. To keep the Flask application running continuously in a production environment, you can use Gunicorn. First, install Gunicorn by running:

    ```bash
    pip install gunicorn
    ```
    Then start the server using the following command:

    ```bash
    nohup gunicorn -w 4 app:app &
    ```
    This will ignore hangup signals and run the Gunicorn process in the background, ensuring the service continues running even after closing the SSH session.