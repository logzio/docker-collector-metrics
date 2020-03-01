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
--env LOGZIO_URL="<LISTENER-URL>" \
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
| **LOGZIO_MODULES** | **Required** The Meatricbeat modules we will use for this container separated by ',' delimiter, formatted as "module1,module2,module3". Currently we support these modules: `system`, `docker`, `aws`. <br /> For further information on supported modules, please see the Supported modules section. <br />If you want to use your custom module configurations or use modules that we are yet to support, you need to mount the module files to `/logzio/modules` |
| **LOGZIO_EXTRA_DIMENSIONS** | include additional fields with every message sent, formatted as "fieldName1=fieldValue1;fieldName2=fieldValue2". To use an environment variable, format as "fieldName1=fieldValue1;fieldName2=$ENV_VAR_NAME". In that case, the environment variable should be the only value in the field. If the environment variable can’t be resolved, the field is omitted.|

<!-- todo list of supported modules -->

#### Supported modules:

| Module | Environment Parameter | Description |
|---|---|---|
| **AWS** | **AWS_ACCESS_KEY** | **Required**. Your AWS account access key ID. |
| | **AWS_SECRET_KEY** | **Required**. Your AWS secret key that matches to the above access key. |
| | **AWS_REGION** | **Required**. Your AWS account region (for example, `us-east-1`). For more information on finding your account's region, see [AWS regions](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html) |
| | **AWS_NAMESPACES** | **Required**. The namespaces of the services you wish to receive metrics from, as specified on [AWS docs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/aws-services-cloudwatch-metrics.html) (for example, `AWS/EC2`). |
| **Docker** | | **Required**: Mount docker.sock to the container itself by adding `-v /var/run/docker.sock:/var/run/docker.sock:ro` to the run command. |
| **System** | | |


### 3. Check Logz.io for your metrics

Run the docker. Give your metrics a few minutes to get from your system to ours, and then open [Kibana](https://app.logz.io/#/dashboard/kibana).

## Change log

 - **0.1.0**:
    - Upgraded to metricbeat 7.5.2.
    - Renamed `LOGZIO_ADDITIONAL_FIELDS` to `LOGZIO_EXTRA_DIMENSIONS`. Dimensions will arrive under `dim`.
    - Deprecated `LOGZIO_URL`. We are now supporting `LOGZIO_REGION`.
    - Added AWS module.
 - **0.0.5**: 
    - Added docker module.
 - **0.0.4**: 
    - Refactor the image to use default Metricbeat yamls.
 - **0.0.3**: BREAKING CHANGES:
    - using beats7
    - supporting multiple modules
 - **0.0.2**: added the ability to set the type to fetched metrics.
