# Docker Metrics Collector - system module

Docker Metrics Collector is an image that runs Metricbeat with the modules you enable at runtime.
If you're not already running Docker Metrics Collector, follow the steps in [Configuration](#configuration) below.

Otherwise, stop the container, add `system` to the `LOGZIO_MODULES` environment variable, and restart.
You can find the `run` command and all parameters in step 2 of the configuration below.

The `system` module collects these metrics:
`cpu`, `diskio`, `filesystem`, `fsstat`, `load`, `memory`, `network`, `process_summary`, 
`process`, `process`, `raid`, `socket_summary`, `socket`, `uptime`
### Configuration

#### 1.  Pull the Docker image

Download the Docker Metrics Collector image:

```shell
docker pull logzio/docker-collector-metrics
```

#### 2.  Run the container

For a complete list of options, see the parameters below the code block.👇

```shell
docker run --name docker-collector-metrics \
--env LOGZIO_TOKEN="<<SHIPPING-TOKEN>>" \
--env LOGZIO_URL="<<LISTENER-HOST>>:5015" \
--env LOGZIO_MODULES="system" \
logzio/docker-collector-metrics
```

**Parameters for all modules**

| Parameter | Description |
|---|---|
| LOGZIO_TOKEN | **Required**. Your Logz.io account token. Replace `<<SHIPPING-TOKEN>>` with the [token](https://app.logz.io/#/dashboard/settings/general) of the account you want to ship to. |
| LOGZIO_URL | **Required**. Logz.io listener URL to ship the metrics to. Replace `<<LISTENER-HOST>>` with your region's listener host (for example, `listener.logz.io`). For more information on finding your account's region, see [Account region](https://docs.logz.io/user-guide/accounts/account-region.html). |
| LOGZIO_MODULES | **Required**. Comma-separated list of Metricbeat modules to be enabled on this container (formatted as `"module1,module2,module3"`). To use a custom module configuration file, mount its folder to `/logzio/logzio_modules`. |
| LOGZIO_TYPE | **Default**: `docker-collector-metrics` <br> The log type you'll use with this Docker. This is shown under the `type` field in Kibana. <br> Logz.io applies parsing based on `type`. |
| LOGZIO_LOG_LEVEL | **Default**: `"INFO"` <br>  The log level the module startup scripts will generate. |
| LOGZIO_ADDITIONAL_FIELDS | Semicolon-separated list of additional fields to be included with each message sent (formatted as `fieldName1=value1;fieldName2=value2`). <br> To use an environment variable as a value, format as `fieldName=$ENV_VAR_NAME`. Environment variables must be the only value in the field. Where an environment variable can't be resolved, the field is omitted. |

**Parameters for System Metrics Collector**

| Parameter | Description |
|---|---|
| **HOSTNAME** | Custom name of the host. <br /> **Default**: `HOSTNAME` environment variable


#### 3.  Check Logz.io for your metrics

Spin up your Docker containers if you haven't done so already.
Give your metrics a few minutes to get from your system to ours, and then open [Kibana](https://app.logz.io/#/dashboard/kibana).
