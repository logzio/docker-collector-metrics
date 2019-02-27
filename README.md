# docker-collector-metrics
This forwards your docker metrics to your [Logz.io](https://app.logz.io/) account using a metricbeat container.
With this collector you can also exclude or include certain containers.
You can also ship docker logs with our [Docker-collector-logs](https://github.com/logzio/docker-collector-logs).  

## How to use the docker collector

To run the docker collector use this command:  
```
docker run --env LOGZIO_TOKEN="{{LOGZIO_TOKEN}}" --env LOGZIO_URL="listener.logz.io:5015" -v /var/run/docker.sock:/var/run/docker.sock:ro logzio/docker-collector-metrics
```
*Change the {{LOGZIO_TOKEN}} to your shipping token*  
*If your account is in the eu region change the LOGZIO_URL enviorenment variable to listener-eu.logz.io:5015*

### Supported enviornment variable

- LOGZIO_TOKEN - your logz.io shipping token
- LOGZIO_URL - either listener-eu.logz.io:5015 or listener.logz.io:5015
- matchContainerName (optional)- a comma separated list of the **only** containers you want the collector to collect the logs from
- skipConatinerName (optional) - a comma separated list of containers you want to exclude
*Only one of match or skip container name can be used*  
*The filtering is done based on a contain operator so you can match part of a value,i.e skipContainerName = "apache,nginx" will skip logs from any container that it's name contains apache or nginx*  

### Metricsets enabled by default
- "container"
- "cpu"
- "diskio"
- "healthcheck"
- "info"
- "memory"
- "network"

### Examples of possible commands

Shipping metrics from containers that their name contains "apache" or "nginx"
```
docker run --env LOGZIO_TOKEN="{{LOGZIO_TOKEN}}" --env LOGZIO_URL="listener.logz.io:5015" --env matchContainerName="apache,nginx" -v /var/run/docker.sock:/var/run/docker.sock:ro logzio/docker-collector-metrics
```

Shipping metrics from all containers except containers that their name contains "jenkins"
```
docker run --env LOGZIO_TOKEN="{{LOGZIO_TOKEN}}" --env LOGZIO_URL="listener.logz.io:5015" --env skipContainerName="jenkins" -v /var/run/docker.sock:/var/run/docker.sock:ro logzio/docker-collector-metrics
```
## How it works
This docker container is using a python script to generate a valid metricbeat configuration file based on your enviornment variables, and then starts the service.  
The container mounts the docker sock to the docker collector container itself so metricbeat will be able to fetch the metrics and the metadata.
