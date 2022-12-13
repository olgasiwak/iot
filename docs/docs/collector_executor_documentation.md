<a id="components.collector_executor"></a>

# collector\_executor
Moduł odpowiedzialny za zbieranie informacji publikowanych przez sensory na odpowiednich topicach w brokerze mosquitto i sterowanie na ich podstawie zapalaniem lamp.
Zebrane informacje przekazywane są do modułu data2metric odpowiedzialnego za agregację i archiwizację informacji z sieci.

<a id="components.collector_executor.Module"></a>

## Module Objects

```python
class CollectorExecutor()
```
Moduł odpowiedzialny za zbieranie informacji z sensorów i sterowanie zapalaniem lamp

<a id="components.collector_executor.Module.change_lamps_states"></a>

#### change\_lamps\_states

```python
def change_lamps_states(lamp)
```
Metoda podejmująca decyzję o zaświeceniu lub zgaszeniu lamp na podstawie informacji o stanie sensora

**Arguments**:

- `lamp` (`Lamp`): Obiekt klasy Lamp() zawierający informację o nazwie topicu grupy lamp i pożądnym stanie (ON/OFF) danej grupy

<a id="components.collector_executor.Module.send_on_signal"></a>

#### send\_on\_signal

```python
def send_on_signal(lamp_name)
```
Metoda publikująca informację o konieczności zaświecenia danej grupy lamp, na topic odpowiadający danej grupie lamp

**Arguments**:

- `lamp_name` (`String`): Nazwa topicu z którego przyszła informacja o konieczności zmiany stanu lamp

<a id="components.collector_executor.Module.send_off_signal"></a>

#### send\_off\_signal

```python
def send_off_signal(lamp_name)
```
Metoda publikująca informację o konieczności zgaszenia danej grupy lamp, na topic odpowiadający danej grupie lamp

**Arguments**:

- `lamp_name` (`String`): Nazwa topicu z którego przyszła informacja o konieczności zmiany stanu lamp

<a id="components.collector_executor.Module.prepare_topic_name"></a>

#### prepare\_topic\_name

```python
def prepare_topic_name(lamp_name)
```
Metoda wyliczająca nazwę topicu do sterowania daną grupą lamp na podstawie nazwy topicu z którego przyszła informacja o stanie grupy sensorów

**Arguments**:

- `lamp_name` (`String`): Nazwa topicu z którego przyszła informacja o stanie grupy sensorów  

<a id="components.collector_executor.Module.on_connect"></a>

#### on\_connect

```python
def on_connect(client, userdata, flags, rc)
```
Metoda wywoływana, gdy broker odpowiada na nasze żądanie połaczenia

**Arguments**:

- `client` (`MQTT Client`): Instancja klasy Client
- `userdata` (``): Prywatne dane użytkownika określone w Client() lub user_data_set()
- `flags` (``): Flagi odpowiedzi wysyłane przez brokera
- `rc` (`int`): wynik połączenia 0: Połączenie pomyślne 1: Połączenie odrzucone - niewłaściwa wersja protokołu 2: Połączenie odrzucone - nieprawidłowy identyfikator klienta 3: Połączenie odrzucone - serwer niedostępny 4: Połączenie odrzucone - zła nazwa użytkownika lub hasło 5: Połączenie odrzucone - brak autoryzacji 6-255: Obecnie nieużywane.

<a id="components.collector_executor.Module.on_message"></a>

#### on\_message

```python
def on_message(client, userdata, msg)
```
Wywoływana, gdy odebrano wiadomość na topic subskrybowany przez klienta

**Arguments**:

- `client` (`MQTT Client`): Instancja klasy Client
- `userdata` (``): Prywatne dane użytkownika określone w CLient() lub user_data_set()
- `msg` (``): Instancja MQTTMessage

<a id="components.collector_executor.Module.notify_executor"></a>

#### notify\_executor

```python
def notify_executor(lamp)
```

Metoda wysyłająca informację do executora w celu przełączenia stanu lampy na podstawie informacji z czujników

**Arguments**:

- `lamp` (`Lamp`): Obiekt klasy Lampy() z informacją o nazwie topicu na który publikuje dana grupa sensorów i stanie grupy sensorów (obecność lub brak ruchu)

<a id="components.collector_executor.Module.notify_data_to_metric"></a>

#### notify\_data\_to\_metric

```python
def notify_data_to_metric(states, polling_cycle)
```
Metoda wysyłająca informacje o stanie sensorów do modułu data2metric

**Arguments**:

- `states` (`int`): Stan sensorów (0/1)
- `polling_cycle` (`int`): Okres czasu co jaki informacje o stanie sensorów powinny być zapisywane

<a id="components.collector_executor.Module.main"></a>

#### start_listening_loop

```python
def start_listening_loop()
```
Główna metoda konfigurująca klienta Paho MQTT i rozpoczynająca nasłuch informacji od sensorów na odpowiednich topicach

<a id="components.config"></a>


<a id="components.lamp"></a>

# Lamp

<a id="components.lamp.LampState"></a>

## LampState Objects

```python
class LampState(int, Enum)
```

Enum zawierający reprezentację możliwych stanów lamp ON - 1, OFF - 0

<a id="components.lamp.Lamp"></a>

## Lamp Objects

```python
class Lamp()
```

Klasa będąca reprezentacją grupy lamp/sensorów

<a id="components.lamp.Lamp.__init__"></a>

#### \_\_init\_\_

```python
def __init__(name: str, state: LampState) -> None
```

**Arguments**:

- `name` (`String`): Nazwa grupy lamp
- `state` (`LampState`): Stan lamp ON/OFF


# config


Plik zawierający parametry konfiguracyjne dla modułu collector_executor

- `MQTT_ADDRESS` - Adres brokera MQTT
- `MQTT_PORT` - Port na którym uruchominoy jest broker MQTT
- `MQTT_TIMEOUT` - Wartość limitu czasu utrzymywania aktywności dla klienta
- `ENCODING` - Kodowanie znaków
- `BACKUP_STATEFILE` - Nazwa pliku do którego zrzucany jest ostatni znany stan sieci w sytuacji zatrzymania działani programu
- `TOPIC_SENSORS_COLLECTOR_REGEX` - Regex nazw topiców na których publikują sensory
- `TOPIC_EXECUTOR_SENSORS_REGEX` - Regex nazw topiców na które subskrybują się lampy
- `INFLUX_ORG` - Nazwa organizacji w InfluxDB
- `INFLUX_URL` - Adres InfluxDB
- `INFLUX_BUCKET` - Nazwa bucketa w InfluxDB
- `INFLUX_TOKEN` - Lokalizacja tokenu do połączenia się z bazą InfluxDB
- `DATA2METRIC_POLLING_CYCLE` - Okres czasu co jaki zapisywane są informacje o stanie sieci
- `logger` - Konfiguracja loggera



