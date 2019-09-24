# docker-collector-metrics

docker-collector-metrics is a Docker container that uses Metricbeat to collect metrics and forward those metrics to your Logz.io account.

To use this container, you'll set environment variables in your docker run command.
docker-collector-metrics uses those environment variables to specify which Metricbeat modules you want to be collected.
docker-collector-metrics mounts docker.sock to the container itself, allowing Metricbeat to collect the metrics and metadata.

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
--env LOGZIO_MODULES="<COLLECTED-MODULES>" \
logzio/docker-collector-metrics
```

#### Parameters

| Parameter | Description |
|---|---|
| **LOGZIO_TOKEN** | **Required**. Your Logz.io account token. Replace `<ACCOUNT-TOKEN>` with the [token](https://app.logz.io/#/dashboard/settings/general) of the account you want to ship to. |
| **LOGZIO_URL** | **Default**: listener.logz.io <br /> Logz.io listener URL to ship the metrics to. For more information on finding your account's region, see [Account region](https://docs.logz.io/user-guide/accounts/account-region.html).|
| **LOGZIO_TYPE** | **Default**: `docker-collector-metrics` <br /> Logz.io type you'll use with this Docker. This is shown in your logs under the `type` field in Kibana. Logz.io applies parsing based on type. |
| **LOGZIO_LOG_LEVEL** | **Default**: `"INFO"` <br /> The log level the scripts will use|
| **LOGZIO_MODULES** | **Required** The Meatricbeat modules we will use for this container separated by ',' delimiter, formatted as "module1,module2,module3". Current we support these modules: `system`, `docker` <br /> If you specify the `docker` module, you'll have to mounts docker.sock to the container itself by adding `-v /var/run/docker.sock:/var/run/docker.sock:ro` to the run command. <br /> If you want to use your custom module configurations or use modules that we are yet to support, you need to mount the module files to `/logzio/modules`|
| **LOGZIO_ADDITIONAL_FIELDS** | include additional fields with every message sent, formatted as "fieldName1=fieldValue1;fieldName2=fieldValue2". To use an environment variable, format as "fieldName1=fieldValue1;fieldName2=$ENV_VAR_NAME". In that case, the environment variable should be the only value in the field. If the environment variable can’t be resolved, the field is omitted.|

<!-- todo list of supported modules -->

### 3. Check Logz.io for your metrics

Run the docker. Give your metrics a few minutes to get from your system to ours, and then open [Kibana](https://app.logz.io/#/dashboard/kibana).

## Change log
 - **0.0.4**: 
    - Refactor the image to use default Metricbeat yamls.
 - **0.0.3**: BREAKING CHANGES:
    - using beats7
    - supporting multiple modules
 - **0.0.2**: added the ability to set the type to fetched metrics.
