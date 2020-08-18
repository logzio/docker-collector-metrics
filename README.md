# Docker Metrics Collector

To simplify shipping metrics from one or many sources,
we created Docker Metrics Collector.
Docker Metrics Collector is a container
that runs Metricbeat with the modules you enable at runtime.

Docker Metrics Collector ships metrics only.
If you want to ship logs to Logz.io,
see [docker-collector-logs](https://github.com/logzio/docker-collector-logs).

## Configuration

### 1. Pull the Docker image

Download the Docker Metrics Collector image:

```shell
docker pull logzio/docker-collector-metrics
```

### 2. Run the container

You'll set your configuration using environment variables
in the `docker run` command.
Each parameter is formatted like this:
`--env ENV_VARIABLE_NAME="value"`.

For a complete list of options, see the parameters below the code block
and in the [_Modules_](#modules) section at the bottom of this doc. 👇

```shell
docker run --name docker-collector-metrics \
--env LOGZIO_TOKEN="<<SHIPPING-TOKEN>>" \
--env LOGZIO_MODULES="<<MODULES>>" \
logzio/docker-collector-metrics
```

**Note**:
Documentation for specific modules is covered
in the [_Modules_](#modules) section at the bottom of this doc.

#### Parameters for all modules

| Parameter | Description |
|---|---|
| LOGZIO_TOKEN (Required) | Your Logz.io account token. Replace `<<SHIPPING-TOKEN>>` with the [token](https://app.logz.io/#/dashboard/settings/general) of the account you want to ship to. <!-- logzio-inject:account-token --> |
| LOGZIO_MODULES (Required) | Comma-separated list of Metricbeat modules to be enabled on this container (formatted as `"module1,module2,module3"`). To use a custom module configuration file, mount its folder to `/logzio/logzio_modules`. |
| LOGZIO_REGION | Two-letter region code, or blank for US East (Northern Virginia). This determines your listener URL (where you're shipping the logs to) and API URL. <br> You can find your region code in the [Regions and URLs](https://docs.logz.io/user-guide/accounts/account-region.html#regions-and-urls) table. |
| LOGZIO_TYPE (Default: `docker-collector-metrics`) | This field is needed only if you're shipping metrics to Kibana and you want to override the default value. <br> In Kibana, this is shown in the `type` field. Logz.io applies parsing based on `type`. |
| LOGZIO_LOG_LEVEL (Default: `"INFO"`) | The log level the module startup scripts will generate. |
| LOGZIO_EXTRA_DIMENSIONS | Semicolon-separated list of dimensions to be included with your metrics (formatted as `dimensionName1=value1;dimensionName2=value2`). <br> To use an environment variable as a value, format as `dimensionName=$ENV_VAR_NAME`. Environment variables must be the only value in the field. If an environment variable can't be resolved, the field is omitted. |
| DEBUG (Default: `false`) | Set to `true` if you want Metricbeat to run in debug mode.<br/> **Note:** Debug mode tends to generate a lot of debugging output, so you should probably enable it temporarily only when an error occurs while running the docker-collector in production.  |
| HOSTNAME (Default: `''`) | Insert your host name if you want it to appear in the metrics' `host.name`. If no value entered,  `host.name` will show the container's id. |

### 3. Check Logz.io for your metrics

Give your metrics a few minutes to get from your system to ours,
and then open [Logz.io](https://app.logz.io/#/dashboard/kibana).

You can view your metrics in Grafana.
We offer preconfigured dashboards for several sources,
which you can find by clicking **<i class="fas fa-th-large"></i> > Manage**
in the left menu.

## Modules

### Docker module

If you're collecting metrics from your Docker containers,
you'll need to include `docker` in the `LOGZIO_MODULES` environment variable
and to mount `docker.sock` at runtime.

For example:

```shell
docker run --name docker-collector-metrics \
--env LOGZIO_TOKEN="<<SHIPPING-TOKEN>>" \
--env LOGZIO_MODULES="docker" \
-v /var/run/docker.sock:/var/run/docker.sock:ro \
logzio/docker-collector-metrics
```

#### Parameters for the Docker module

| Parameter | Description |
|---|---|
| DOCKER_MATCH_CONTAINER_NAME | Comma-separated list of containers you want to collect the metrics from. If a container's name partially matches a name on the list, that container's metrics are shipped. Otherwise, its metrics are ignored. <br> **Note**: Can't be used with `DOCKER_SKIP_CONTAINER_NAME`. |
| DOCKER_SKIP_CONTAINER_NAME | Comma-separated list of containers you want to ignore. If a container's name partially matches a name on the list, that container's metrics are ignored. Otherwise, its metrics are shipped. <br> **Note**: Can't be used with `DOCKER_MATCH_CONTAINER_NAME`. |
| DOCKER_PERIOD (Default: `10s`) | Sampling rate of metrics. The Docker API takes up to 2 seconds to respond, so we recommend setting this to `3s` or longer. |
| DOCKER_CERTIFICATE_AUTHORITY | Filepath to certificate authority for connecting to Docker over TLS. |
| DOCKER_CERTIFICATE | Filepath to CA certificate for connecting to Docker over TLS. |
| DOCKER_KEY | Filepath to Docker key for connecting to Docker over TLS. |

### AWS module

For the AWS module,
you'll need to include `aws` in the `LOGZIO_MODULES` environment variable.

For example:

```shell
docker run --name docker-collector-metrics \
--env LOGZIO_TOKEN="<<SHIPPING-TOKEN>>" \
--env LOGZIO_MODULES="aws" \
--env AWS_ACCESS_KEY="<<ACCESS-KEY>>" \
--env AWS_SECRET_KEY="<<SECRET-KEY>>" \
--env AWS_REGION="<<AWS-REGION>>" \
--env AWS_NAMESPACES="<<NAMESPACES>>" \
logzio/docker-collector-metrics
```

You'll also need to set up an IAM user
with the permissions to fetch the right metrics,
and the region you're fetching metrics from.

#### Region configuration

You'll need to specify the AWS region you're collecting metrics from.

![AWS region menu](https://dytvr9ot2sszz.cloudfront.net/logz-docs/aws/region-menu.png)

Find your region's slug in the region menu
(in the top menu, on the right side).

For example:
The slug for US East (N. Virginia)
is "us-east-1",
and the slug for Canada (Central) is "ca-central-1".

Paste your region slug in your text editor.
You'll need this for your Metricbeat configuration later.

#### Parameters for the AWS module

| Parameter | Description |
|---|---|
| AWS_ACCESS_KEY (Required) | Your IAM user's access key ID. |
| AWS_SECRET_KEY (Required) | Your IAM user's secret key. |
| AWS_REGION (Required) | Your region's slug. You can find this in the AWS region menu (in the top menu, to the right). |
| AWS_NAMESPACES (Required) | Comma-separated list of namespaces of the metrics you want to collect. <br> You can find a complete list of namespaces at [_AWS Services That Publish CloudWatch Metrics_](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/aws-services-cloudwatch-metrics.html) |

### System module

**Note**:
This Docker container monitors Linux system metrics only.
For other OSes, we recommend [running Metricbeat locally](https://docs.logz.io/shipping/metrics-sources/system.html) on the system itself.

For the system module,
you'll need to include `system` in the `LOGZIO_MODULES` environment variable.

Use this to monitor Linux systems only, for other types of system like OSX/Windows use [Metricbeat locally](https://docs.logz.io/shipping/metrics-sources/system.html).

For example:

```shell
docker run --name docker-collector-metrics \
--env LOGZIO_TOKEN="<<SHIPPING-TOKEN>>" \
--env LOGZIO_MODULES="system" \
--volume="/var/run/docker.sock:/var/run/docker.sock:ro" \
--volume="/sys/fs/cgroup:/hostfs/sys/fs/cgroup:ro" \
--volume="/proc:/hostfs/proc:ro" \
--volume="/:/hostfs:ro" \
--net=host \
logzio/docker-collector-metrics
```

## Change log
 - **0.1.5**:
    - Supports adding hostname.
 - **0.1.4**:
    - Supporting debug mode.
 - **0.1.3**:
    - Updated new public SSL certificate in Docker image & Metricbeat configuration.
 - **0.1.2**:
    - Pulling metrics from custom AWS namespaces.
 - **0.1.1**:
    - Pulling tags from AWS services.
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
