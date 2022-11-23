FROM python:3.7-slim

COPY requirements.txt ./requirements.txt

ENV LOGZIO_DIR_PATH /logzio
ENV LOGZIO_MODULES_PATH ${LOGZIO_DIR_PATH}/modules


RUN apt-get update && apt-get install --no-install-recommends -y wget && \
    rm -rf /var/lib/apt/lists/* && \ 
    wget --quiet https://artifacts.elastic.co/downloads/beats/metricbeat/metricbeat-7.10.0-amd64.deb && \
    dpkg -i metricbeat-7.10.0-amd64.deb && \
    rm metricbeat-7.10.0-amd64.deb && \
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
