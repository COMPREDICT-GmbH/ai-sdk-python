COMPREDICT's AI CORE API Client
===============================

Python client for connecting to the COMPREDICT V1 REST API.

To find out more, visit COMPREDICT website:
https://compredict.ai/ai-core/

Requirements
------------

**To connect to the API with basic auth you need the following:**

- API Key taken from COMPREDICT's User Dashboard
- (Optional) Callback url to send the results
- (Optional) Private key for decrypting the messages.

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

### Basic Auth
~~~python
import compredict

compredict_client = compredict.client.api.get_instance(token=token, callback_url=None, ppk=None, passphrase="")
~~~

We highly advice that the SDK information are stored as environment variables.

Accessing Algorithms (GET)
--------------------------

To list all the algorithms in a collection:

~~~python
algorithms = compredict_client.getAlgorithms()

for algorithm in algorithms:
    print(algorithm.name)
    print(algorithm.version)
~~~

To access a single algorithm:

~~~python
algorithm = compredict_client.getAlgorithm('ecolife')

print(algorithm.name)
print(algorithm.description)
~~~

Algorithm RUN (POST)
--------------------

Any algorithm a user has access to is different, it has different:

- Input data and structure.
- Output data.
- Evaluation set.
- Result instance.
- Accepted file format.

The `run` function has the following signature: 

~~~python
Task|Result = algorithm.run(data, evaluate=True, encrypt=False, callback_url=None, 
                            callback_param=None, file_content_type=None)
~~~

- `data`: data to be processed by the algorithm, it can be:
   - `dict`: forces the file's content type to be `application/json`
   - `str`: path to the file to be sent, set the `file_content_type` to the mime type or empty for `application/json`
   - `pandas`: DataFrame containing the data, set the `file_content_type` to convert the content to appropriate file. 
- `evaluate`: to evaluate the result of the algorithm. Check `algorithm.evaluations`, *more in depth later*.
- `encrypt`: to encrypt the data using RSA AES, *more in depth later*.
- `callback_url`: If the result is `Task`, then AI core will send back the results to the provided URL once processed. It can be multiple callbacks
- `callback_param`: additional parameters to pass when results are sent to callback url. In case of multiple callbacks, it can be a single callback params for all, or multiple callback params for each callback url.
- `file_content_type`: The type of data to be sent. Based on `algorithm.accepted_file_format`. it could be:
    - `application/json`: for dict data.
    - `text/csv`: when passing pandas DataFrame.
    - `application/parquet`: when passing pandas's DataFrame.
    
Depending on the algorithm's computation requirement `algorithm.result`, the result can be:

- **compredict.resources.Task**: holds a job id of the task that the user can query later to get the results.
- **compredict.resources.Result**: contains the result of the algorithm + evaluation

**Create list of urls for callbacks**

~~~python
callback_url = ["https://me.myportal.cloudapp.azure.com", "http://me.mydata.s3.amazonaws.com/my_bucket",
                "http://my_website/my_data.com"]
~~~
After creating a list, use it when running algorithm:

~~~python
results = algorithm.run(data, callback_url=callback_url, evaluate=False, encrypt=True)
~~~ 

**Example of sending data as `application/json`:**

~~~python
X_test = dict(
    feature_1=[1, 2, 3, 4],
    feature_2=[2, 3, 4, 5]
)

algorithm = compredict_client.getAlgorithm('algorithm_id')
result = algorithm.run(X_test)
~~~

You can identify when the algorithm dispatches the processing to queue
or send the results instantly by checking:

~~~python
>>> print(algorithm.results)
The request will be sent to queue for processing
~~~

or dynamically:

~~~python
results = algorithm.predict(X_test, evaluate=True)

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

**Example of sending data as `application/parquet`:**

~~~python
import pandas as pd

X_test = pd.DataFrame(dict(
    feature_1=[1, 2, 3, 4],
    feature_2=[2, 3, 4, 5]
))

algorithm = compredict_client.getAlgorithm('algorithm_id')
result = algorithm.run(X_test, file_content_type="application/parquet")
~~~

**Example of sending data from parquet file:**

~~~python
algorithm = compredict_client.getAlgorithm('algorithm_id')
result = algorithm.run("/path/to/file.parquet", file_content_type="application/parquet")
~~~

If you set up ``callback_url`` then the results will be POSTed automatically to you once the
calculation is finished.

Each algorithm has its own evaluation methods that are used to evaluate the performance of the algorithm given the data. You can identify the evaluation metric
by calling:

~~~python
algorithm.evaluations  # associative array.
~~~

When running the algorithm, with `evaluate = True`, then the algorithm will be evaluated by the default parameters. In order to tweek these parameters, you have to specify an associative array with the modified parameters. For example:

~~~python
evaluate = {"rainflow-counting": {"hysteresis": 0.2, "N":100000}} # evaluate name and its params

result = algorithm.predict(X_test, evaluate=evaluate)
~~~

Data Privacy
------------

When the calculation is queued in COMPREDICT, the result of the calculations will be stored temporarily for three days. If the data is private and there are organizational issues in keeping this data stored in COMPREDICT, then you can encrypt the data using RSA. COMPREDICT allow user's to add RSA public key in the Dashboard. Then, COMPREDICT will use the public key to encrypt the stored results. In return, The SDK will use the provided private key to decrypt the returned results.

COMPREDICT will only encrypt the results when:

- The user provide a public key in the dashboard.
- Specify **encrypt** parameter in the predict function as True.

Here is an example:
~~~python
# First, you should provide public key in COMPREDICT's dashboard.

# Second, Call predict and set encrypt as True
results = algorithm.predict(X_test, evaluate=True, encrypt=True)

if isinstance(results, resources.Task):
    if results.status is results.STATUS_FINISHED:
        print(results.is_encrypted)
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
algorithms = compredict_client.getAlgorithms()

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
compredict_client.failOnError()

try:
    orders = compredict_client.getAlgorithms()
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
compredict_client.verifyPeer(false)
~~~
