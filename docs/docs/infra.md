# Infrastruktura chmurowa projektu

System po stronie software'owej został uruchomiony na maszynach wirtualnych z GNU/Linux - dystrybucji Ubuntu 20.04.5 LTS.
Maszyny hostowane są na platformie chmurowej Linode.
Tworzenie i utrzymanie maszyn zostało zautomatyzowane z użyciem narzędzia Terraform ([strona narzędzia](https://www.terraform.io)).
Skrypt, którym uruchomione zostały maszyny jest umieszczony w repozytorium Git pod ścieżką `iot/scripts/automation/infrastructure.tf`.

## Maszyny i ich przeznaczenie
System składa się z 5 maszyn wirtualnych, wg projektu architektury systemu.

## Broker
Maszyna wirtualna, gdzie uruchomione są kontenery z brokerem MQTT ([strona narzędzia](https://mosquitto.org)) oraz z własną implementacją kolektora z kolejek brokera.

## Maszyna wizualizacyjna
Maszyna wirtualna, na której uruchomione są kontenery Docker z narzędziem Grafana ([strona narzędzia)(https://grafana.com)) oraz bazą time-series InfluxDB ([strona narzędzia](https://www.influxdata.com)).

## Discoverer
Maszyna wirtualna, na której uruchomione są baza danych nazwana przez projekt AssetDB, która bazuje na PostgreSQL ([strona narzędzia](https://www.postgresql.org)), a także API opisane w dokumentacji.

## Klient1 i Klient2
Maszyny wirtualne do testowania i uruchamiania generatora sztucznego ruchu.
