import influxdb_client, os, time, random
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

class InfluxClient():
    def __init__(self, org, url, bucket, token):
        self.org = org
        self.url = url
        self.bucket = bucket
        self.token = token
        self.client = influxdb_client.InfluxDBClient(url=self.url,
                                                     token=self.token,
                                                     org=self.org
                                                     )

    def prepare_single_sensor_datapoints(self, states):
        for state in states:
            states[state] = int(states[state])
        points = [Point(f'sensor{sensor[-1:]}').field('is_active', states[sensor]) for sensor in states]
        return points

    def prepare_active_lanterns_ratio_datapoint(self, states):
        for state in states:
            states[state] = int(states[state])
        point = (
              Point(f'sensors_stats')
              .field('active_lanterns_ratio',(sum((states.values())) / len(states)))
              )
        return point

    def write_to_database(self, points):
        write_api = self.client.write_api(write_options=SYNCHRONOUS)
        for point in points:
            write_api.write(
                    bucket=self.bucket,
                    org=self.org,
                    record=point
                    )
