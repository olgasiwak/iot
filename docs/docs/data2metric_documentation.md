# data2metric
Moduł konwertujący dane pochodzące z sensorów do odpowiednich metryk, a następnie zapisujący je do bazy InfluxDB.

<a id="components.data2metric.InfluxClient"></a>
## Metody w klasie InfluxClient()

```python
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
```

<a id="components.data2metric.InfluxClient.prepare_single_sensor_datapoints"></a>

#### def prepare\_single\_sensor\_datapoints

```python
def prepare_single_sensor_datapoints(states):
        for state in states:
            states[state] = int(states[state])
        points = [Point(f'sensor{sensor[-1:]}').field('is_active', states[sensor]) for sensor in states]
        return points
```
Metoda przygotowywująca punkt pomiarowe (Point) z informację o stanie pojedynczej grupy sensorów.

**Arguments**:

- `states` (`array(int)`): Informacja o stanie grupy sensorów

<a id="components.data2metric.InfluxClient.prepare_active_lanterns_ratio_datapoint"></a>

#### def prepare\_active\_lanterns\_ratio\_datapoint

```python
def prepare_active_lanterns_ratio_datapoint(states):
        for state in states:
            states[state] = int(states[state])
        point = (
              Point(f'sensors_stats')
              .field('active_lanterns_ratio',(sum((states.values())) / len(states)))
              )
        return point
```
Metoda przygotowywująca punkt pomiarowe (Point) z informację o stosunku włączonych do wyłączonych sensorów.

**Arguments**:

- `states` (`array(int)`): Stany sensorów

<a id="components.data2metric.InfluxClient.write_to_database"></a>

#### def write\_to\_database

```python
def write_to_database(points):
        write_api = self.client.write_api(write_options=SYNCHRONOUS)
        for point in points:
            write_api.write(
                    bucket=self.bucket,
                    org=self.org,
                    record=point
                    )
```
Metoda zapisująca stworzone punkty pomiarowe (Point) do bazy danych.
 
**Arguments**:

- `points` (`Point()`): Punkty pomiarowe (Obiekty klasy Point())
