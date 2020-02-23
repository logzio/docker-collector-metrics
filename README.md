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

For a complete list of options, see the parameters below the code block
and in the [_Modules_](#modules) section at the bottom of this doc. 👇

```shell
docker run --name docker-collector-metrics \
--env LOGZIO_TOKEN="<<SHIPPING-TOKEN>>" \
--env LOGZIO_URL="<<LISTENER-HOST>>" \
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
| LOGZIO_URL (Default: `listener.logz.io`) | Logz.io listener host to ship the metrics to. Replace `<<LISTENER-HOST>>` with your region's listener host (for example, `listener.logz.io`). For more information on finding your account's region, see [Account region](https://docs.logz.io/user-guide/accounts/account-region.html). |
| LOGZIO_TYPE (Default: `docker-collector-metrics`) | This field is needed only if you're shipping metrics to Kibana and you want to override the default value. <br> In Kibana, this is shown in the `type` field. Logz.io applies parsing based on `type`. |
| LOGZIO_LOG_LEVEL (Default: `"INFO"`) | The log level the module startup scripts will generate. |
| LOGZIO_EXTRA_DIMENSIONS | Semicolon-separated list of dimensions to be included with your metrics (formatted as `dimensionName1=value1;dimensionName2=value2`). <br> To use an environment variable as a value, format as `dimensionName=$ENV_VAR_NAME`. Environment variables must be the only value in the field. If an environment variable can't be resolved, the field is omitted. |

<!-- #### Supported modules:

| Module | Environment Parameter | Description |
|---|---|---|
| **AWS** | **AWS_ACCESS_KEY** | **Required**. Your AWS account access key ID. |
| | **AWS_SECRET_KEY** | **Required**. Your AWS secret key that matches to the above access key. |
| | **AWS_REGION** | **Required**. Your AWS account region (for example, `us-east-1`). For more information on finding your account's region, see [AWS regions](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html) |
| | **AWS_NAMESPACES** | **Required**. The namespaces of the services you wish to receive metrics from, as specified on [AWS docs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/aws-services-cloudwatch-metrics.html) (for example, `AWS/EC2`). |
| **Docker** | | **Required**: Mount docker.sock to the container itself by adding `-v /var/run/docker.sock:/var/run/docker.sock:ro` to the run command. |
| **System** | | | -->

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
--env LOGZIO_URL="<<LISTENER-HOST>>" \
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
--env LOGZIO_URL="<<LISTENER-HOST>>" \
--env LOGZIO_MODULES="aws" \
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
| AWS_NAMESPACES (Required) | The namespaces of the metrics you want to collect. <br> You can find a complete list of namespaces at [_AWS Services That Publish CloudWatch Metrics_](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/aws-services-cloudwatch-metrics.html) |

### System module

For the system module,
you'll need to include `aws` in the `LOGZIO_MODULES` environment variable.

For example:

```shell
docker run --name docker-collector-metrics \
--env LOGZIO_TOKEN="<<SHIPPING-TOKEN>>" \
--env LOGZIO_URL="<<LISTENER-HOST>>" \
--env LOGZIO_MODULES="system" \
logzio/docker-collector-metrics
```

## Change log

 - **0.1.0**:
    - Upgraded to metricbeat 7.5.2.
    - Added AWS module.
    - Renamed `LOGZIO_ADDITIONAL_FIELDS` to `LOGZIO_EXTRA_DIMENSIONS`. Dimensions will arrive under `dim`.
 - **0.0.5**: 
    - Added docker module.
 - **0.0.4**: 
    - Refactor the image to use default Metricbeat yamls.
 - **0.0.3**: BREAKING CHANGES:
    - using beats7
    - supporting multiple modules
 - **0.0.2**: added the ability to set the type to fetched metrics.
