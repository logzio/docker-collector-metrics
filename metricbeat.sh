#!/usr/bin/env bash

# Script to run Metricbeat in foreground with the same path settings that
# the init script / systemd unit file would do.

exec /opt/metricbeat/metricbeat \
  -path.home /opt/metricbeat \
  -path.config /etc/metricbeat \
  -path.data /opt/metricbeat \
  -path.logs /opt/metricbeat \
  "$@"
