FROM python:3.7-slim

COPY requirements.txt ./requirements.txt

RUN apt-get update && \
    apt-get install -y \
    curl \
    wget && \
    curl -L -O https://artifacts.elastic.co/downloads/beats/metricbeat/metricbeat-6.5.4-amd64.deb && \
    dpkg -i metricbeat-6.5.4-amd64.deb && \
    rm metricbeat-6.5.4-amd64.deb && \
    wget https://raw.githubusercontent.com/logzio/public-certificates/master/COMODORSADomainValidationSecureServerCA.crt && \
    mkdir -p /etc/pki/tls/certs && \
    cp COMODORSADomainValidationSecureServerCA.crt /etc/pki/tls/certs/ && \
    rm COMODORSADomainValidationSecureServerCA.crt && \
    pip install -r requirements.txt && \
    rm requirements.txt

COPY default_metricbeat.yml ./default_metricbeat.yml
COPY metricbeat-yml-script.py ./metricbeat-yml-script.py

CMD ["python","metricbeat-yml-script.py"]
