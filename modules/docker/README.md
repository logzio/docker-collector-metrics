# docker module
By default, docker ,module enable `container`, `cpu`, `diskio`, `healthcheck`, `info`, `memory`, and `network` metrics.

#### Parameters

| Parameter | Description |
|---|---|
| **DOCKER_SKIP_CONTAINER_NAME** | Comma-separated list of containers you want to ignore. If a container’s name partially matches a name on the list, that container’s logs are ignored. Otherwise, its logs are shipped. **Note**: Can’t be used with matchContainerName |
| **DOCKER_MATCH_CONTAINER_NAME** | Comma-separated list of containers you want to collect the logs from. If a container’s name partially matches a name on the list, that container’s logs are shipped. Otherwise, its logs are ignored. **Note**: Can’t be used with skipContainerName |
| **DOCKER_PERIOD** | **Default**: `10s` <br /> It is strongly recommended that you run Docker metricsets with a period that is 3 seconds or longer. The request to the Docker API already takes up to 2 seconds. Specifying less than 3 seconds will result in requests that timeout, and no data will be reported for those requests. |
| **DOCKER_CERTIFICATE_AUTHORITY** | **Example**: `/etc/pki/root/ca.pem` <br /> Certificate authority for connecting to docker over TLS with a CA certificate|
| **DOCKER_CERTIFICATE** | **Example**: `/etc/pki/client/cert.pem` <br /> Certificate for connecting to docker over TLS with a CA certificate|
| **DOCKER_KEY** | **Example**: `/etc/pki/client/cert.key` <br /> Key for connecting to docker over TLS with a CA certificate|
| **DOCKER_CPU_PER_CORE** | **Default**: `true` <br /> If set to true, collects metrics per core.|

