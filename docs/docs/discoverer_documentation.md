# Discoverer

Moduł **Discoverer** ma na celu obsługiwać nowe urządzenia IoT podłączane do systemu. Do jego funkcjonalności należą:

* Identyfikacja urządzenia,
* Zlecenie skonfigurowania dostępu do **brokera**,
* Skonfigurowanie nowego urządzenia.

## Abstract

**Discoverer** nasłuchuje na nowe zgłoszenia na topiku zefiniowanym jako `BROKER_DISCOVERY_TOPIC`. Podłączające się do systemu nowe urządzenie wysyła zapytanie na ww. topik. Każde nowe zgłoszenie jest obsługiwane w osobnym wątku.

> **Uwaga:**
> Z powodu GIL'a Python *de facto* nie zrównolegla zadań, co w przyszłości może powodować problem z wydajnością. Porponowane rozwiązanie to zmiana na async albo Go ;)

Każde zgłoszenie - `hello_message` musi zawierać informacje niezbędne do zidentyfikowania urządzenia: `MAC address` oraz unikalny identyfikator w systemie - `UDID`, ułożone w struktue formatu JSON:

```json
{
    "mac": <str: MAC address>,
    "udid": <str: UDID>
}
```

Na podstawie tych wartości są wykonywane następujące kroki:

1. Sparawdzamy czy w bazie **AssetDB** jest urządzenie o zadanym `MAC`'u i `UDID`, patrz `handle_hello_message(...)`,
2. Pobieramy z bazy konfigurację dla grupy do której dane urządzenie należy, patrz `send_configuration(...)`,
3. Na dedykowany danemu urządzeniu topik konfiguracyjny `BROKER_CONFIGURATION_TOPIC` wysyłamy konfigurację w formacie JSON, patrz `send_configuration(...)`. 

```json
{
    "lower_threshold": <float>,
    "upper_threshold": <float>
}
```

## Zaleności

**Discoverer** bezpośrednio komunikuje się i zależy od następujących modułów systemu:

* **Broker** - **Discoverer** subskrybuje `BROKER_DISCOVERY_TOPIC` i publukuje na `BROKER_CONFIGURATION_TOPIC`. Szczegóły przesylanych wiadomości są wymienione powżyej. Konfiguracja połączenia jest poprzez zmienne `BROKER_*`,
* **AssetDB** - stanowi *source of truth* dla **Discoverer**'a, który pobiera dane bezpośrednio z bazy wykorzystując sqlalchemy ORM, patrz `models.py`. Konfiguracja połączenia jest poprzez zmienne `POSTGRESQL_DB_*`,
* **Guardian** - jest uruchomiany przy starcie **Discoverer**'a i otrzymuje zlecenie konfiguracje dostępu do **brokera**, szczegóły są w dedykowanym rozdziale dokumntacji ;  

## Known issues

* brak walidacji dla wartości konfigów `0 < x <= 1`

### TODO
