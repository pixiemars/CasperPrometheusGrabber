# Casper Prometheus Grabber
Parse various casper endpoints into prometheus client

## Requirements/Dependencies

StatusNodePromGrab.py requires **python 3**  to be installed and the following dependencies:

 - [requests](https://docs.python-requests.org/en/master/)
 - [prometheus_client](https://github.com/prometheus/client_python)
 - [twisted](https://twistedmatrix.com/trac/)

  `pip3 install requests prometheus_client twisted`

## Configuration
There are 3 variables you can configure at the top of StatusNodePromGrab.py
Set the url to your casper node status endpoint:

    endpoint_url = "http://localhost:8888/status"
Set your refresh interval in seconds, at some point this will become more intelligent based on average block times:

    interval = 60

Set the port you wish to run the service on:

    default_port = 8123


## Running in a terminal
This will run as a standard python cli script using twisted's reactor to serve it

    python3 StatusNodePromGrab.py

## Running headless using twistd (better for running as a service)

If you want to run as a headless application for use as a daemon then Twisted's **twisd** is better. To run under twistd simply run the command below in your shell, shell script, cron job or systemd etc.

    twistd3 -y StatusNodePromGrab.py

[For info on deployment using **systemd** please click here :)](https://docs.twistedmatrix.com/en/twisted-20.3.0/core/howto/systemd.html)