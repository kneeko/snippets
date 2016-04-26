## snippets

A simple key-value store application with human-readable keys.

## Setup
Install [Google App Engine SDK for Python](https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python).

Create a new project in the [console](https://console.developers.google.com/).

Clone the repository and deploy to your new project.

    appcfg.py update . --application your_project_id

## Usage

This application is intended to be a straight-forward way to store arbitrary data as part of another program.

### Storing data

We can store data by making an HTTP POST request which returns a human-readable key in plaintext.

	$ curl -X -POST --data "arbitrary data" https://your_project_id.appspot.com
    24-graceful-crocodiles-meandered-sadly

### Retrieving data

We can retrieve data by making an HTTP GET request which returns our data in plaintext.

    $ curl https://your_project_id.appspot.com/24-graceful-crocodiles-meandered-sadly
    arbitrary data

### Extras

We can specify a key using the path of the request. The request will fail if the key is already in use.

	$ curl -X -POST --data "more arbitrary data" https://your_project_id.appspot.com/some-specific-key
    some-specific-key

You can get a list of all the stored keys delineated by newline. This is useful for manually looking at the data coming in, but not much else.

	$ curl https://your_project_id.appspot.com/list
    24-graceful-crocodiles-meandered-sadly
    some-specific-key

In `app.yaml` there are some parameters you can set.

    env_variables:
        EXPIRE_SNIPPETS: False
        EXPIRATION_TIME_IN_DAYS: 31
        MAX_BYTES_PER_SNIPPET: 1048576
        ALLOW_UUID_OVERRIDE: True
        READS_PER_MINUTE: 60
        WRITES_PER_MINUTE: 10
        LISTS_PER_MINUTE: 10

- You can set the maximum size of the data. The default is 1MB.
- You can enable expiration and set the expiration time. A cron will run every 24 hours and delete key-value pairs that exceed the expiration time.
- You can configure rate limiting by IP address. This won't be enough to stop someone determined to abuse your instance of this application. If you are being targeted, it will be more effect to use Google App Engine's [built in DoS protection](https://cloud.google.com/appengine/docs/python/config/dos).
- You can disable the ability to specify a key. If you disable this, all requests with a specified key will fail.
