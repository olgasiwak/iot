FROM python
WORKDIR /collector_executor
COPY ./collector /collector_executor
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "/collector_executor/collector_executor.py"]

ENV INFLUXDB_TOKEN $INFLUXDB_TOKEN
