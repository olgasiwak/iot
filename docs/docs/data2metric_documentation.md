# data2metric

<a id="components.data2metric.InfluxClient"></a>

## InfluxClient Objects

```python
class InfluxClient()
```

<a id="components.data2metric.InfluxClient.prepare_single_sensor_datapoints"></a>

#### prepare\_single\_sensor\_datapoints

```python
def prepare_single_sensor_datapoints(states)
```
Metoda przygotowywyująca punkt pomiarowe (Point) z informację o stanie pojedynczej grupy sensorów

**Arguments**:

- `states` (`array(int)`): Informacja o stanie grupy sensorów

<a id="components.data2metric.InfluxClient.prepare_active_lanterns_ratio_datapoint"></a>

#### prepare\_active\_lanterns\_ratio\_datapoint

```python
def prepare_active_lanterns_ratio_datapoint(states)
```
Metoda przygotowywyująca punkt pomiarowe (Point) z informację o stosunku włączonych do wyłączonych sensorów

**Arguments**:

- `states` (`array(int)`): Stany sensorów

<a id="components.data2metric.InfluxClient.write_to_database"></a>

#### write\_to\_database

```python
def write_to_database(points)
```
Metoda zapisująca stworzone punkty pomiarowe (Point) do bazy danych
 
**Arguments**:

- `points` (`Point()`): Punkty pomiarowe (Obiekty klasy Point())
