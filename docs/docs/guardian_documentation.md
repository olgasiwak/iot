# Guardian

Głównym zadaniem modułu **Guardian** jest zarządzanie dostępem do **brokera** poprzez configurację list dostępowych **broker**'a.
Jest to moliwe dzięki plugin'u <a href= https://mosquitto.org/documentation/dynamic-security/>`dynamic security`</a>.

**Guardian** definiuje dwie główne abstrakcje umożliwiające granularne sterowanie dostępem:

* **Role** : `roles` - dla każdego urządzniena osobna, patrz `create_roles_for_devices(...)`; dla modułu **Discovery** i domyślną z ograniczonym dostępem, patrz `create_default_roles(...)`. Rola definiuje do jakich topików i w jakim zakresie będzie miał dostęp posiada danej roli,
* **Klienci** : `clients` - przypisuje każde z urządzeń do konkretnej roli.

## Jak to działa?

Urządzenia są identyfikowane na podstawie `username`:`password`, które dla uproszczenia są ustawiane na wartość `UDID`. Urządzenie bez zdefiniowanego klienta trafia do tzw. `anonymous_group` z ograniczonym dostępem do **brokera**. Jest to zrobione po to, żeby klient mógł łatwiej debugować problemy z dostępem.

W uproszczeniu wygląda to tak:

```bash
      IoT Device (UDID:UDID)
                ||
                \/
Dynamic security Client (user:password)
                ||
                \/
  Dynamic security Role (role_name)
                ||
                \/
               ACLs
```

## Kod
Kod w większości stanowi wrappery do API **brokera**. Więcej informacji o tych funkcjach można znaleźć w <a href= https://mosquitto.org/documentation/dynamic-security/>`dokumnetacji plugin'a`</a>

## Czemu nie przydzielać ról dynamicznie?

Dynamiczne tworzenie ról dla nowych urządzeń oznacza, że w momencie kiedy nowe urządzenie się zgładsza do **Discoverer**'a ono nie ma przydzielonej roli, czyli trafia do `anonymous_group`. **Discvoverer** - dynamicznie reagując na nowe zgłoszenie - mógłby tworzyć role i przydzielać klientów, ale to by wymagało odświerzenia połączenia ze strony klienta. Co utrudnia komunikację i jest sprzeczne z koncepcją działania systemów kolejkowych.

Natomiast **AssetDB** pozwala nam skonfigurować dostęp dla wszystkich znanych urządzeń w momencie startu systemu, usuwając czynnik dynamiczny i osiągając ten sam wynik.

## Known issues

* A co jeśli w trakcie działania systemu dodamy nowe devicy do bazy?
