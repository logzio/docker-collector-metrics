FROM arm32v7/python:3.7-slim

COPY requirements.txt ./requirements.txt

ENV PACKAGE=metricbeat-7.5.2-linux-arm32v7.tar.gz
ENV METRICBEAT_DIR=/opt/metricbeat
ENV METRICBEAT_CONFIG_DIR=/etc/metricbeat
ENV LOGZIO_DIR_PATH /logzio
ENV LOGZIO_MODULES_PATH ${LOGZIO_DIR_PATH}/modules

COPY $PACKAGE $PACKAGE
COPY metricbeat.sh /usr/bin/metricbeat

RUN apt-get update && \
    apt-get install -y curl wget && \
    mkdir -p $METRICBEAT_DIR && \
    mkdir -p $METRICBEAT_CONFIG_DIR && \
    tar --no-same-owner --strip-components=1 -zxf "$PACKAGE" -C $METRICBEAT_DIR && \
    mv $METRICBEAT_DIR/metricbeat.yml $METRICBEAT_CONFIG_DIR && \
    rm -f "$PACKAGE" && \
    wget https://raw.githubusercontent.com/logzio/public-certificates/master/TrustExternalCARoot_and_USERTrustRSAAAACA.crt && \
    mkdir -p /etc/pki/tls/certs && \
    cp TrustExternalCARoot_and_USERTrustRSAAAACA.crt /etc/pki/tls/certs/ && \
    rm TrustExternalCARoot_and_USERTrustRSAAAACA.crt && \
    pip install -r requirements.txt && \
    rm requirements.txt && \
    mkdir -p ${LOGZIO_DIR_PATH}

COPY modules ${LOGZIO_MODULES_PATH}
COPY metricbeat.yml ${LOGZIO_DIR_PATH}/
COPY metricbeat-yml-script.py ${LOGZIO_DIR_PATH}/

WORKDIR ${LOGZIO_DIR_PATH}
CMD python metricbeat-yml-script.py
