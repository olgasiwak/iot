# Wybór wykorzystanej technologii

W celu zapisywania danych o urządzeniach w sieci IoT potrzebowaliśmy bazy, 
która będzie prosta, nie spodziewamy się wykonywać się na niej żadnych złożonych operacji.
Zdecydowaliśmy się na PostgreSQL. <br>
Rozważane bazy:
 - PostgreSQL - łatwa w użycia, doświadczenie zespołu z tym rozwiązaniem
 - MariaDB - nie jest w pełni kompatybilna  z SQL
 - SQLite - łatwa w użyciu, jednak posiada pewne ograniczenia i brakuje jej kilku kluczowych funkcji 
np. pozwala na zapisywanie do bazy przez maksymalnie 1 użytkownika jednocześnie.

W celu zapisywania danych o zebranych przez czujniki ruchu potrzebowaliśmy bazy danych
zoptymalizowanej pod kątem działania na danych zorientowanych na czas. Zdecydowaliśmy się na InfluxDB. 
Rozważane bazy timeseries:
 - InfluxDB -  obsługuje zarówno dane numeryczne jak i tekstowe, język zbliżone doskładni SQL. 
Rozwiązanie darmowe, open source oraz łatwo w implementacji
 - Prometheus - obsługuje tylko dane numerycznie, język typowy dla rozwiązań NoSQL. 
Rozwiązanie darmowe oraz open source.
 - TimescaleDB - pozwala na złożone typy danych, budowanie dużych, rozbudowanych zapytań. 
Wspiera język SQL, rozwiązanie darmowa oraz open source.

Przy wyborze narzędzie do wizualizacji zależało nam na znalezieniu narzędzia, 
które pozwoli na integrację danych z PostgreSQL oraz InfluxDB, pozwoli na tworzenie własnych,
rozbudowanych widoków, definiowanie alarmów, które pomogłyby w monitoringu sieci oraz było darmowe. 
Wszystkie te kryteria spełnia Grafana, poza nią rozważaliśmy też:
 - Power BI - brak wsparcie dla InfluxDB, dane na widokach odświeżają się razdziennie
 - Kibana - pozwala na integrację wyłącznie Elasticsearcha, brak możliwości alarmowania