COMPREDICT's AI CORE API Client
===============================

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/COMPREDICT-GmbH/ai-sdk-python/ai-sdk-python)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/COMPREDICT-GmbH/ai-sdk-python)
[![PyPI](https://img.shields.io/pypi/v/COMPREDICT-AI-SDK?color=orange)](https://pypi.org/project/COMPREDICT-AI-SDK/)

**Python client for connecting to the COMPREDICT V2 REST API.**

**To find out more, please visit** **[COMPREDICT website](https://compredict.ai/ai-core/)**.


Requirements
------------

**To connect to the API with basic auth you need the following:**

- Token generated with your AI Core username and password
- (Optional) Callback url to send the results

Installation
------------

You can use `pip` or `easy-install` to install the package:

~~~shell
 $ pip install COMPREDICT-AI-SDK
~~~

or

~~~shell
 $ easy-install COMPREDICT-AI-SDK
~~~

Configuration
-------------

### Basic Authentication

AI Core requires from the user, to authenticate with token, generated with user's AI CORE username and password.

**WARNING**: Bear in mind, that this type of authentication is working only for v2 of AI Core API.

**There are two ways in which user can generate needed token:**

1. **Generate token directly with utility function** (this approach requires user to pass url to AICore as well):
~~~python
from compredict.utils.authentications import generate_token

# user_username and user_password in this example, are of course credentials personal to each user
response = generate_token(url="https://core.compredict.ai/api/v2", username=user_username, 
                                     password=user_password)
response_json = response.json()

# access tokens or errors encountered
if response.status_code == 200:
    token = response_json['access']
    refresh_token = response_json['refresh']
    print(token)
    print(refresh_token)
elif response.status_code == 400:
    print(response_json['errors'])
else:
    print(response_json['error'])
~~~

Now, you can instantiate Client with freshly generated token.
~~~python
import compredict

compredict_client = compredict.client.api.get_instance(token=your_new_generated_token_here)
~~~

2. **Instantiate Client with your AICore username and password.** In this case, token, as well as refresh_token, will be 
   generated and assigned automatically to the Client. After this operation, you don't need to reinstantiate Client 
   with generated token. You should be able to directly call all Client methods as you like.
~~~python
import compredict

compredict_client = compredict.client.api.get_instance(username=username, password=password, callback_url=None)
~~~

### Accessing new access token with token refresh
Refresh token is used for generating new access token (mainly in case if previous access token is expired).

**New access token can be generated with refresh token in two ways:**

**1. By calling utility function:**

~~~python
from compredict.utils.authentications import generate_token_from_refresh_token

response = generate_token_from_refresh_token(url="https://core.compredict.ai/api/v2", token=refresh_token)
response_json = response.json()

# access token or errors encountered
if response.status_code == 200:
    token = response_json['access']
    print(token)
elif response.status_code == 400:
    print(response_json['errors'])
else:
    print(response_json['error'])
~~~
Then, you can instantiate Client with new access token.

**2. By calling Client method:**

If you generated token with passing to the Client your username and password, you don't need to pass
your refresh_token to generate_token_from_refresh_token() Client method, since your refresh_token is already stored 
inside the Client.

~~~python
# look above for the explanation in which cases token_to_refresh is not required
token = compredict_client.generate_token_from_refresh_token(refresh_token)
~~~

### Check token validity

If user would like for Client to automatically check token validity while instantiating Client, **validate** needs to 
enabled.
~~~python
import compredict

compredict_client = compredict.client.api.get_instance(token=your_new_generated_token_here, validate=True)
~~~

**User can manually verify token validity in two ways:**

**1. By calling utility function:**
~~~python
from compredict.utils.authentications import verify_token

response = verify_token(url="https://core.compredict.ai/api/v2", token=token_to_verify)

# check validity
if response.status_code == 200:
    print(True)
else:
    print(False)
~~~

**2. By calling Client method:**

If you generated token with passing to the Client your username and password, you don't need to pass
your token to verify_token() Client method, since your token is already stored inside the Client.
~~~python
# look above for the explanation in which cases token_to_verify is not required
validity = compredict_client.verify_token(token_to_verify)
print(validity)
~~~
In case of valid token, response will be empty with status_code 200.

**We highly advice that the SDK information are stored as environment variables.**

Accessing Algorithms (GET)
--------------------------

To list all the algorithms in a collection:

~~~python
algorithms = compredict_client.get_algorithms()

for algorithm in algorithms:
    print(algorithm.name)
    print(algorithm.version)
~~~

To access a single algorithm:

~~~python
algorithm = compredict_client.get_algorithm('ecolife')

print(algorithm.name)
print(algorithm.description)
~~~

Algorithm RUN (POST)
--------------------
Each algorithm, that user has access to, is different. It has different:

- Input data and structure
- Output data
- Parameters data
- Evaluation set
- Result instance
- Monitoring Tools

**Features data, used for prediction, always needs to be provided in parquet file, whereas
parameters data is always provided in json file.** 

**User, taking advantage of this SDK, can specify features in 
dictionary, list of dictionaries, DataFrame or string with path pointing out to parquet file.**

The `run` function has the following signature: 

~~~python
Task|Result = algorithm.run(data, parameters=parameters, evaluate=True, encrypt=False, callback_url=None, 
                            callback_param=None, monitor=True)
~~~

- `features`: data to be processed by the algorithm, it can be:
   - `dict`: will be written into parquet file
   - `str`: path to the file to be sent (only parquet file will be accepted)
   - `pandas`: DataFrame containing the data, will be written into parquet file as well
- `parameters`: Parameters used for configuration of algorithm (specific for each algorithm). It is optional and can be:
    - `dict`: will be converted into json file
    - `str` : path to json file with parameters data
- `evaluate`: to evaluate the result of the algorithm. Check `algorithm.evaluations`, *more in depth later*.
- `callback_url`: If the result is `Task`, then AI core will send back the results to the provided URL once processed. It can be multiple callbacks
- `callback_param`: additional parameters to pass when results are sent to callback url. In case of multiple callbacks, it can be a single callback params for all, or multiple callback params for each callback url.
- `monitor`: boolean indicating if the output results of the model should be monitored or not. By default it is set 
  to True.
    
Depending on the algorithm's computation requirement `algorithm.result`, the result can be:

- **compredict.resources.Task**: holds a job id of the task that the user can query later to get the results.
- **compredict.resources.Result**: contains the result of the algorithm + evaluation + monitors

**Create list of urls for callbacks**

~~~python
callback_url = ["https://me.myportal.cloudapp.azure.com", "http://me.mydata.s3.amazonaws.com/my_bucket",
                "http://my_website/my_data.com"]
~~~
After creating a list, use it when running algorithm:

~~~python
results = algorithm.run(data, callback_url=callback_url, evaluate=False)
~~~ 

**Example of specifying features data in a dictionary and sending it for prediction:**

~~~python
X_test = dict(
    feature_1=[1, 2, 3, 4],
    feature_2=[2, 3, 4, 5]
)

algorithm = compredict_client.get_algorithm('algorithm_id')
result = algorithm.run(X_test)
~~~

You can identify when the algorithm dispatches the processing of task to queue
or sends the results instantly by checking:

~~~python
>>> print(algorithm.results)

"The request will be sent to queue for processing"
~~~

or dynamically:

~~~python
results = algorithm.run(X_test, parameters=parameters, evaluate=True)

if isinstance(results, compredict.resources.Task):
    print(results.job_id)

    while results.status != results.STATUS_FINISHED:
        print("task is not done yet.. waiting...")
        sleep(15)
        results.update()

    if results.success is True:
        print(results.predictions)
    else:
        print(results.error)

else:  # not a Task, it is a Result Instance
    print(results.predictions)
~~~

**Example of specifying features data in DataFrame and sending it for prediction:**

~~~python
import pandas as pd

X_test = pd.DataFrame(dict(
    feature_1=[1, 2, 3, 4],
    feature_2=[2, 3, 4, 5]
))

algorithm = compredict_client.get_algorithm('algorithm_id')
result = algorithm.run(X_test)
~~~

**Example specifying features data directly in parquet file and sending it for prediction:**

~~~python
algorithm = compredict_client.get_algorithm('algorithm_id')
result = algorithm.run("/path/to/file.parquet")
~~~

If you set up ``callback_url`` then the results will be POSTed automatically to you once the
calculation is finished.

Each algorithm has its own evaluation methods that are used to evaluate the performance of the algorithm given the data. You can identify the evaluation metric
by calling:

~~~python
algorithm.evaluations  # associative array.
~~~

When running the algorithm, with `evaluate = True`, then the algorithm will be evaluated by the default parameters. 
In order to tweak these parameters, you have to specify an associative array with the modified parameters. For example:

~~~python
evaluate = {"rainflow-counting": {"hysteresis": 0.2, "N":100000}} # evaluate name and its params

result = algorithm.run(X_test, evaluate=evaluate)
~~~


Handling Errors And Timeouts
----------------------------

For whatever reason, the HTTP requests at the heart of the API may not always
succeed.

Every method will return false if an error occurred, and you should always
check for this before acting on the results of the method call.

In some cases, you may also need to check the reason why the request failed.
This would most often be when you tried to save some data that did not validate
correctly.

~~~python
algorithms = compredict_client.get_algorithms()

if not algorithms:
    error = compredict_client.last_error
~~~

Returning false on errors, and using error objects to provide context is good
for writing quick scripts but is not the most robust solution for larger and
more long-term applications.

An alternative approach to error handling is to configure the API client to
throw exceptions when errors occur. Bear in mind, that if you do this, you will
need to catch and handle the exception in code yourself. The exception throwing
behavior of the client is controlled using the failOnError method:

~~~python
compredict_client.fail_on_error()

try:
    orders = compredict_client.get_algorithms()
raise compredict.exceptions.CompredictError as e:
    ...
~~~

The exceptions thrown are subclasses of Error, representing
client errors and server errors. The API documentation for response codes
contains a list of all the possible error conditions the client may encounter.


Verifying SSL certificates
--------------------------

By default, the client will attempt to verify the SSL certificate used by the
COMPREDICT AI Core. In cases where this is undesirable, or where an unsigned
certificate is being used, you can turn off this behavior using the verifyPeer
switch, which will disable certificate checking on all subsequent requests:

~~~python
compredict_client.verify_peer(False)
~~~
