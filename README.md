COMPREDICT's AI CORE API Client
===============================

Python client for connecting to the COMPREDICT V1 REST API.

To find out more, visit the official documentation website:
https://compredict.de

Requirements
------------

- Python >= 3.4
- Requests >= 2.1.0
- pycrypto >= 1.4.0

**To connect to the API with basic auth you need the following:**

- API Key taken from COMPREDICT's User Dashboard
- Username of the account.
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

We highly advice that the SDK information are stored as environment variables and called used `environ`.

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

Algorithm Prediction (POST)
-----------------------------

Some resources support creation of new items by posting to the collection. This
can be done by passing an array or stdClass object representing the new
resource to the global create method:

~~~python
X_test = dict(
    feature_1=[1, 2, 3, 4],
    feature_2=[2, 3, 4, 5]
)

algorithm = compredict_client.getAlgorithm('algorithm_id')
result = algorithm.run(X_test)
~~~

Depending on the algorithm's computation requirement, the result can be:

- **Task**: holds a job id of the task that the user can query later to get the results.
- **Result**: contains the result of the algorithm + evaluation

You can identify when the algorithm dispatches the processing to queue
or send the results instantly by:

~~~python
print(algorithm.results)
~~~

or dynamically:

~~~python
results = algorithm.predict(X_test, evaluate=True)

if isinstance(results, resources.Task):
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

If you set up ``callback_url`` then the results will be POSTed automatically to you once the
calculation is finished.


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
raise:
    compredict.exceptions.CompredictError as e:
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