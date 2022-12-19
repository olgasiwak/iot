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

## Terraform
Wyżej wspomniany skrypt dla narzędzia terraform został przygotowany w celu automatycznego budowania oraz "niszczenia" infrastruktury. Zdecydowaliśmy się na niego, ponieważ infrastruktura rozrosła się do 5 maszyn wirtualnych.

Skrypt pobiera od użytkownika 2 zmienne na wejściu: klucz do API platformy Linode oraz hasło, które zostanie ustawione dla użytkownika `root`.

```HCL
variable "IOT_API_KEY" {
    type = string
}

variable "root_password" {
  type = string
  sensitive = true
}
```

Następnie zdefiniowano dostawcę chmurowego, dostęp do niego oraz klucz SSH dla zdalnego dostępu do maszyn.

```HCL
terraform {
  required_providers {
    linode = {
      source  = "linode/linode"
    }
  }
}

provider "linode" {
    token = var.IOT_API_KEY
}

resource "linode_sshkey" "ssh_key" {
  label = "ssh_key"
  ssh_key = chomp(file("~/.ssh/iot.pub"))
}
```

Na sam koniec definiujemy kodem maszyny wirtualne.

```HCL
resource "linode_instance" "iot-broker" {
    label = "broker"
    image = "linode/ubuntu20.04"
    region = "us-central"
    type = "g6-standard-1"
    authorized_keys = [linode_sshkey.ssh_key.ssh_key]
    root_pass = var.root_password

    group = "iot"
    tags = [ "iot" ]
    swap_size = 256
    private_ip = true
}
...
```