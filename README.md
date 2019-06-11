# docker-collector-metrics

docker-collector-metrics is a Docker container that uses Metricbeat to collect metrics from other Docker containers and forward those metrics to your Logz.io account.

To use this container, you'll set environment variables in your docker run command.
docker-collector-metrics uses those environment variables to generate a valid Metricbeat configuration for the container.
docker-collector-metrics mounts docker.sock to the container itself, allowing Metricbeat to collect the metrics and metadata.

By default, docker-collector-metrics ships `container`, `cpu`, `diskio`, `healthcheck`, `info`, `memory`, and `network` metrics.

docker-collector-metrics ships metrics only. If you want to ship logs to Logz.io, see [docker-collector-logs](https://github.com/logzio/docker-collector-logs).

## docker-collector-metrics setup

### 1. Pull the Docker image

Download the logzio/docker-collector-metrics image:

```shell
docker pull logzio/docker-collector-metrics
```

### 2. Run the container

For a complete list of options, see the parameters below the code block.👇

```shell
docker run --name docker-collector-metrics \
--env LOGZIO_TOKEN="<ACCOUNT-TOKEN>" \
--env LOGZIO_URL="<LISTENER-URL>:5015" \
-v /var/run/docker.sock:/var/run/docker.sock:ro \
logzio/docker-collector-metrics
```

#### Parameters

| Parameter | Description |
|---|---|
| **LOGZIO_TOKEN** | **Required**. Your Logz.io account token. Replace `<ACCOUNT-TOKEN>` with the [token](https://app.logz.io/#/dashboard/settings/general) of the account you want to ship to. |
| **LOGZIO_URL** | **Required**. Logz.io listener URL to ship the metrics to. This URL changes depending on the region your account is hosted in. For example, accounts in the US region ship to `listener.logz.io`, and accounts in the EU region ship to `listener-eu.logz.io`. <br /> For more information, see [Account region](https://docs.logz.io/user-guide/accounts/account-region.html) on the Logz.io Docs. |
| **matchContainerName** | Comma-separated list of containers you want to collect metrics from. If a container's name partially matches a name on the list, that container's metrics are shipped. Otherwise, its metrics are ignored. <br /> **Note**: Can't be used with `skipContainerName` |
| **skipContainerName** | Comma-separated list of containers you want to ignore. If a container's name partially matches a name on the list, that container's metrics are ignored. Otherwise, its metrics are shipped. <br /> **Note**: Can't be used with `matchContainerName` |

**Note**: By default, metrics from `docker-collector-logs` and `docker-collector-metrics` containers are ignored.

### 3. Check Logz.io for your metrics

Spin up your Docker containers if you haven’t done so already. Give your metrics a few minutes to get from your system to ours, and then open [Kibana](https://app.logz.io/#/dashboard/kibana).
