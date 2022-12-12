# Grafana

Do wizualizacji informacji odnośnie stanu sieci użyte zostało narzędzi o nazwie Grafan. Stworzony dashboard dostępny jest pod adresem:

[IoT Dashboard Grafana](http://139.144.44.134:3000/d/5HUMlnH4z/iot-dashboard?orgId=1)

Posiada on intergację zarówno z bazą danych InfluxDB, zawierającą informację o dokonanych pomiarach, jak i Postgress, z informacją
o urządzeniach w sieci i ich konfiguracji.

## Skład przygotowanej tablicy:

### Historia aktywności sensorów
Wykres ten zawiera informacje o stanach sensorów (a tym samym lamp) w ciągu ostatnich 7 dni. Na osi x ostaczony został czas, natomiast
oś zawiera poszczególne grupy sensorów. Po wybraniu konkretnego fragmentu wykresu wyświetlana jest szczegółowa informacja na temat czasu
przez jaki grupa sensorów znajdywała się w danym stanie (zarówno sumaryczny czas, jaki dokładna data początku i końca danego stanu). Istnieje 
mozliwość dodania adnotacji do konkretnego fragmentu wykresu.

```flux
from(bucket: "IoT")
|> range(start: -7d, stop: now())
|> filter(fn: (r) => r["_measurement"] =~ /sensor*/ and r._field == "is_active")
|> set(key: "_field", value: "status")
```


![Screenshot](../img/grafana_documentation/Sensors_activity_history.png)

### Ustawienia sensorów/lamp
Tabela zawiera informacje na temat ustawień poszczególnych urządzeń w sieci. Pojedynczy wiersz zawiera:
- informacje na temat wartości unikalnie identyfikujących dane urządzenie, takich jak ID, UDID oraz adres MAC
- informacje odnoście lokalizacji danego urządzenia (longitude, latitude)
- numeru wersji urządzenia
- ustawień jasności lampy przypisanej do danego urządzenia - wartości do jakich dana lampa się rozjaśnia/przygasza (wraz z wizualną reprezentacją)
- identyfikatora grupy do której należy dane urządzenie - Device group ID

```sql
SELECT
  devices.id,devices.UDID,devices.MAC,devices.longitude,devices.latitude,devices.version_id,groups.configuration -> 'lower_threshold' AS lower_bound, groups.configuration -> 'upper_threshold' AS upper_bound, devices.group_id 
FROM devices 
INNER JOIN groups ON groups.id=devices.group_id;
```

![Screenshot](../img/grafana_documentation/Sensors_settings.png)

### Aktualnie aktywne sensory/zapalone latarnie
Gauge zawierający informację o stosunku aktualnie aktywnych urządzeń, do wszystkich urządzeń, jakie obecnie zainstalowane są w sieci

```flux
from(bucket: "IoT")
|> range(start: -1h, stop: now())
|> filter(fn: (r) => r["_measurement"] == "sensors_stats" or r.field == "active_lanterns_ratio")
|> yield(name: "last")

```

![Screenshot](../img/grafana_documentation/Currently_active_sensors.png)

### Ustawienia grupy sensorów
Tabela zawiera informacje o konfiguracji grupy sensorów. Pojedynczy wiersz zawiera:
- ID unikalanie identyfikujące grupę urządzeń
- Description z opisem dotyczącym danej grupy
- Client ID identyfikujące klienta do którego należy dany grupa urządzeń
- ustawienia jasności lamp należących do danej grupy  - wartości do jakich dana grupa lamp się rozjaśnia/przygasza (wraz z wizualną reprezentacją)
- liczba urządzeń w danej grupie

```sql
SELECT
  id, description, client_id, groups.configuration -> 'lower_threshold' AS lower_bound, groups.configuration -> 'upper_threshold' AS upper_bound, quantity
FROM groups;
```

![Screenshot](../img/grafana_documentation/Sensors_group_settings.png)

### Alarmy
Tabela zawiera informacje o alarmach ustawionych w sieci i ich stanach. Dla każdej grupy sensorów znajdującej się w sieci sprawdzamy jej aktywność w ciągu ostatnich 24h.
Jeśli sumaryczny czas świecenia lamp w ciągu ostatniej doby wyniósł 24h, to uznajemy że urządzenie uległa awarii i generujemy
adekwatny alarm, który wyświetlany jest klientowi. Jeśli klient uzna, że takie zachowanie jest pożądane to istnieje możliwość
zignorowania takiego alarmu.

```flux
from(bucket: "IoT")
|> range(start: -1d, stop: now())
|> filter(fn: (r) => r["_measurement"] =~ /sensor*/ and r._field == "is_active")	
|> rename(columns: {_measurement: "sensors_groups"})

```

![Screenshot](../img/grafana_documentation/Alarms.png)

### Mapa
Mapa zawiera informacje o lokalizacji każdego sensora w sieci. Po wybraniu konkretengo sensora otrzymujemy informacje:
- o jego współrzędnych geograficznych,
- identyfikatorach urządzenia
- identyfikatora grupy urządzeń
- ustawień poziomów jasności lampy

```sql
SELECT
  devices.latitude, devices.longitude, devices.id,devices.UDID,devices.MAC, devices.group_id, groups.configuration -> 'lower_threshold' AS brightness_lower_bound, groups.configuration -> 'upper_threshold' AS brightness_upper_bound
FROM devices 
INNER JOIN groups ON groups.id=devices.group_id;

```

![Screenshot](../img/grafana_documentation/Map.png)