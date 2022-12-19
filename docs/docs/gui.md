# Interfejs użytkownika 
## Wstęp

Aplikacja została wykonana przy użyciu technologii Angular 13, biblioteki Bootstrap 5 oraz komponentu Angular Google Maps.
Celem aplikacji jest umożliwienie klientom aktualizacji poziomu rozświetlenia poszczególnych grup latarni. Poprzez komunikację z interfejsem API możliwe jest pobranie i wysłanie informacji na temat latarni. 

## Instalacja

Aby uruchomić aplikację należy najpierw zainstalować potrzebne moduły za pomocą komendy
```
$ npm install
```
a następnie uruchomić serwer komendą
```
$ ng serve
```
Aplikacja uruchamia się pod adresem `http://localhost:4200/`

## Komponenty

#### 1. AppComponent

Komponent główny aplikacji stanowiący kontener dla komponentów podrzędnych i umożliwiający routing między nimi.

#### 2. MapComponent

W tym komponencie wykorzystano zewnętrzny komponent Angular Google Maps, który pozwala na wyświetlenie mapy z zaznaczonymi na niej punktami. W MapComponent pobierane i wyświetlane są informacje o grupach i urządzeniach.

#### 3. ListComponent

Komponent, w którym wyświetlana jest lista grup wraz z informacjami na ich temat.

## Integracja z API

Komunikacja z metodami API jest możliwa dzięki utworzonym serwisom, w których znajdują się metody odpowiadające za wysyłanie zapytań HTTP do API.
Wykorzystywane metody w projekcie:

<img width="600" alt="image" src="https://user-images.githubusercontent.com/44203473/208313363-d2281a01-2cd4-4bee-8a0f-7850932af220.png">

## Działanie
Po uruchomieniu aplikacji domyślnym widokiem jest mapa.
Komponent Angular Google Maps implementuje Google Maps JavaScript API. 

```html
<agm-map *ngIf="devices && latitude_map" [zoom]="12" [latitude]="latitude_map" [longitude]="+devices[0].longitude">
  <agm-marker clickable *ngFor="let device of devices; let i = index" [latitude]="+device.latitude"
     [longitude]="+device.longitude" (markerClick)="showInfo(device)" [iconUrl]="device.icon">
  </agm-marker>
</agm-map>
```

Powyższy kod służy do wyświetlania na stronie mapy ze środkiem w określonej w komponencie długości i szerokości geograficznej oraz zaznaczonymi punktami, w których znajdują się urządzenia. Po kliknięciu w marker wyświetlane są informacje o grupie urządzeń.

<img width="1512" alt="image" src="https://user-images.githubusercontent.com/44203473/208313544-361db080-e3c0-4f14-b3eb-5c999265c3a0.png">

Przycisk “Zobacz statystyki” przekierowuje użytkownika na stronę Grafany, gdzie znajduje się wizualizacja informacji odnośnie stanu sieci.

Po kliknięciu przycisku “Zmień” wyświetlany jest suwak służący do zmiany wartości rozświetlenia grupy.

<img width="428" alt="image" src="https://user-images.githubusercontent.com/44203473/208313570-7b758a83-b01e-46f5-abd0-79fe5065ec6d.png">

Przycisk “Zapisz” pozwala na zapisanie zmian za pomocą metody `saveChanges()`:

```typescript
 saveChanges() {
   this.api.putGroup(this.findGroup.id, this.sliderValue/100).subscribe(() => {
   },
   error => console.log(error),
   () => {
     this.getGroups();
     this.getDevices();
     this.getGroup(this.findGroup.id)
   });
 }
```

Widok listy zawiera informacje o grupach i należących do nich sensorów. Działanie przycisku “Zmień” jest takie samo jak w przypadku mapy.

<img width="1505" alt="image" src="https://user-images.githubusercontent.com/44203473/208313625-b8610e4e-3c2e-4926-b5e8-633b5c5ff84d.png">

