# Generator

Aby wygenerować sztuczny ruch pieszych dla więcej niż jednego sensora, przygotowany został generator ruchu,
osadzony na hoście `client2`. Jest to narzędzie wywoływane z linii komend CLI, któremu zadajemy parametr pogody, pory roku oraz pory dnia. 

Podgląd możliwych do wywołania parametrów:

```bash
python3 traffic_simulator.py --help
usage: Parse parameters to determine possible traffic [-h] [--best | --worst]
                                                      [{autumn,winter,spring,summer,default}]
                                                      [{morning,dusk,evening,night,default}]
                                                      [{windy,rainy,snowy,cloudy,default}]

positional arguments:
  {autumn,winter,spring,summer,default}
                        Season of the year
  {morning,dusk,evening,night,default}
                        Time of the day
  {windy,rainy,snowy,cloudy,default}
                        Present weather

optional arguments:
  -h, --help            show this help message and exit
  --best                Best possible conditions
  --worst               Worst possible conditions
  --rate                Set custom rate of detection
```

Podając warunki opisane w komendzie uzyskujemy wartość na podstawie której obliczamy prawdopodobieństwo wylosowania `1` (w danym oknie czasowym pieszy przeszedł pod czujnikiem ruchu, co spowodowało rozświetlenie latarnii do poziomu zadanego przez użytkownika). Następnie na podstawie wylosowanego prawdopodobieństwa obliczamy prawdopodobieństwo wylosowania `0` (czujka nie wykryła ruchu). Jest to prosty rachunek `1 - P(1)`.

## Wagi parametrów

Wagi poszczególnych parametrów pogody, pory roku oraz pory dnia zostały podane w pliku `weights.yaml` i wyglądają następująco:

```yaml
season:
  winter: 1
  autumn: 2
  spring: 4
  summer: 5
  default: 3

daytime:
  night: 1
  dusk: 2
  morning: 4
  evening: 5
  default: 3

weather:
  rainy: 1
  snowy: 2
  windy: 4
  cloudy: 5
  default: 3
```

Jest to zwykły plik w formacie YAML (Yet Another Markup Language), który zawiera wagi z zakresu `1-5`. Waga `3` została zarezerwowana dla parametru `default`, który występuje wtedy, kiedy użytkownik nie zadał danego parametru na wejściu programu. Im większa waga, tym większe prawdopodobieństwo wystąpienia pieszego, z tego powodu na przykład pora roku `summer` ma większą wagę niż pora roku `winter`.

Prawdopodobieństwo wystąpienia `1` przeliczane jest w następujący sposób:
```
suma wag / 18 (a tak właściwie liczba parametrów * 6)
```

Za pomocą sumy wag nie jesteśmy w stanie osiągnąć prawdopodobieństwa wystąpienia `1` równego 1. Jest to zabieg celowy, ponieważ nie zakładamy sytuacji, że lampa będzie cały czas rozświetlona, co oznaczałoby, że cały czas przechodzą pod nią piesi (niezależnie od pory dnia czy roku). Tak samo z wartością 0, zakładamy, że zawsze jest możliwość pojawienia się pieszego.

## Flagi narzędzia

Aby osiągnąć prawdopodobieństwo równe 1, został zaprojektowany przełącznik `--rate`, który pozwala ustawić dowolne prawdopodobieństwo z przedziału `<0;1>`.

Zaprojektowano również przełączniki `--best` i `--worst`, które generują warunku najlepsze i najgorsze warunki zadane parametrami. Ułatwia to testowanie, ponieważ możemy pominąć wpisywanie wielu parametrów, zastępując je jedną flagą.

## Funkcje w kodzie generatora

Implementacja rozwiązania wymagana stworzenia następujących funkcji w języku Python3.

### def parse_args()

Funkcja pobierająca argumenty z wiersza poleceń oraz zwracająca ich wartości do programu.

```python
def parse_args():
    parser = ArgumentParser('Parse parameters to determine possible traffic')
    group = parser.add_mutually_exclusive_group(required=False)
    parser.add_argument(
            'season',
            choices=['autumn', 'winter', 'spring', 'summer', 'default'],
            help='Season of the year',
            default='default',
            nargs='?',
            type=str
            )
    ...
    return parser.parse_args()
```

### def load_conditions()

Funkcja wczytująca plik YAML z wagami, łapiąca wyjątki oraz zwracająca jego zparsowaną wersję w formie słownika dla programu.

```python
def load_conditions():
    with open(config.WEIGHTS_FILE, 'r') as weights_file:
        try:
            return yaml.safe_load(weights_file)
        except YAMLError as error:
            print(error)
```

### def determine_weights(args, conditions)

Funkcja ustalająca sumę wag podanych na wejściu programu przez użytkownika.

```python
def determine_weight(args, conditions):
    weight = 0
    if args.worst:
        return len(conditions)
    elif args.best:
        return 5 * len(conditions)
    elif args.rate:
        if 0 <= args.rate <= 1:
            return args.rate * 6 * len(conditions)
        else:
            raise ValueError("Rate has to be in range 0-1")
    else:
        for condition in conditions:
            weight += conditions[condition][eval(f'args.{condition}')]
    return weight
```

### def updata_states(STATES, sensor, choice)

Funkcja przygotowująca wartości (stany czujnika) `1` i `0` do wysłania do brokera MQTT oraz zliczająca statystyki.

```python
def update_states(STATES, sensor, choice):
    if sensor not in STATES:
        STATES[sensor] = choice
        STATES[f'current{sensor}'] = choice
    else:
        STATES[sensor] += choice
        STATES[f'current{sensor}'] = choice
    return STATES
```

### def display_states(STATES)

Funkcja wyświetlająca na STDOUT informacje o danej iteracji generowania danych. Stosuje kolorowe wyświetlanie stanów.

```python
def display_states(STATES):
    print('\033[92m' + 50*'-' + '\n')
    for i in range(config.NUMBER_OF_SENSORS):
        print('\033[91m' +
                f'Current state of sensor number {i}: ' +
                str(STATES[f'current{i}']) +
                '\033[0m')
        print('\033[91m' +
                f'Sum of pedestrians detected by sensor number {i}: ' +
                str(STATES[i]) +
                '\033[0m')
        print(10*'-')
    print('\n')
```

### def start_simulator(client, conditions, weight, STATES)

Funkcja startująca symulację, losująca wartości stanu oraz wysyłająca wiadomości co 4 sekundy do broketa MQTT.

```python
def start_simulator(client, conditions, weight, STATES):
    tmp = weight
    while True:
        for i in range(config.NUMBER_OF_SENSORS):
            if i in config.DESOLATED_SENSORS:
                weight /= 2
            choice = choices([1, 0],
                    weights = [(weight/(2*3*len(conditions))),
                    1 - (weight/(3*2*len(conditions)))])[0]
            STATES = update_states(STATES, i, choice)
            client.publish(f"{config.SIMULATOR_SENSORS_PATTERN}{i}", choice)
            weight = tmp
        display_states(STATES)
        time.sleep(4)
```

### def on_connect orad on_message

Funkcje znane z collectora_execurota, doimplementowane do połączenia z brokerem MQTT.

### def main()

Funkcja główna, wywoływana przez program, nawiązuje połączenie z brokerem, losuje wagi i zaczyna symulację.

```python
def main():
    args = parse_args()
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(
            config.MQTT_ADDRESS,
            config.MQTT_PORT,
            config.MQTT_TIMEOUT
            )
    conditions = load_conditions()
    weight = determine_weight(args, conditions)

    start_simulator(client,conditions, weight, STATES)
```

## Konfiguracja

Narzędzie zawiera plik konfiguracyjny zawierający następujące parametry:

- `MQTT_ADDRESS` - Adres brokera MQTT
- `MQTT_PORT` - Port na którym uruchomiony jest broker MQTT
- `MQTT_TIMEOUT` - Wartość limitu czasu utrzymania aktywności dla klienta
- `SIMULATOR_SENSORS_PATTERN` - Regexp nazw topiców na które publikuje generator
- `WEIGHTS_FILE` - Plik zawierający wagi
- `NUMBER_OF_SENSORS` - Liczba sensorów dla których będziemy generować ruch
- `DESOLATED_SENSORS` - Lista sensorów dla których zaniżymy generowany ruch, mogą "symulować" sensory zepsute

