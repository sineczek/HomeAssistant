# Moja Historia

---
**MENU:**

- [Home Assistant](https://github.com/sineczek/HomeAssistant/)
- [Pod Maską](https://github.com/sineczek/HomeAssistant/blob/master/www/pod_maska.md)
- [Node-Red](https://github.com/sineczek/HomeAssistant/blob/master/www/nodered.md)

---
## Początki

Swoją przygodę z Inteligentnym domem zacząłem na przełomie 2018 i 2019 roku. Od początku wiedziałem, że chcę aby mój system działał lokalnie, bez wysyłania informacji do przyjaciół z Chin. Google i Apple wiedzą już wystarczajaco dużo ...
Przygodę rozpocząłem od Domoticza postawionego na Raspberry Pi B+, które posiadałem od 2013 roku do zabaw z kopaniem BTC. Szybko okazało się, że sprzęt ten jest już wolny i trochę zawodny. Nadaszła pora na zmianę w styczniu 2019 roku. Domoticz wylądował na Raspberry Pi 3B+ z 32GB kartą SD. 
Wówczas już, po rozeznaniu się w istniejących technologiach, podjąłem decyzje, że mój MądryDom (MD) będzie funkcjonować z urządzeniami Wi-Fi, RF oraz technologią Z-Wave, która wówczas wydawała mi się o niebo lepsza od ZigBee.
Zakupiłem kilka Sonoff'ów Basic oraz gniazdek S20, i rozpocząłęm swoje testy. Na pierwszy ogień poszedł alternatywy firmware wspomnianych Sonoff'ów. Z Holandi, tfu! z Niderlandów, przyszedł moduł RF oparty na Andruino oraz na pokładzie zagościł Aeotec Z-Stick Gen5 - moduł Z-Wave USB, zaś po okazyjnej cenie z Chin przypłynęły gniazdka Neo Coolcam NAS-WR01ZE Z-wave Plus Smart Power Plug EU Socket. Niestety od razu były z nimi problemy, a współpraca z Domoticzem prawie nie możliwa. Rozpocząłem poszukiwania nowych rozwiązań.

## HA

W marcu 2019 po raz pierwszy Centrum Dowodzenia MD spotkało Home Assistanta i zagościło na karcie SD w RPi 3B+. Jak prawie każdy z użytkowników wie, karty SD w RPi są "lekko kłopotliwe" z punktu widzenia niezawodności przy bazach danych (i dużych ilościach ruchu n karcie). Tak nie mogło być dalej skoro chciałem, aby system był niezawodny! 

> ___ciekawostka:___
>w ciągu 4 miesięcy uszkodziło się 7 kart SD (Samsung, Kingstone, Sandisk), o pojemności od 8 do 32GB. 

Nastąpiły pirwsze większe przenosiny. Home Assistant v0.9 wylądował na dysku SSD bootowalnym z RPi3B+. Ta prędkośc! ta niezawodność! byłem zachwycony!
Równocześnie ze zmianami w sercu systemu, cały ekosystem domu rozwijał się. Doszły kolejne urządzenia z-wave (czujnik dymy, czujnik gazu, kontaktron), rozwinęła się baza elementów opartych na chipie ESP8266 oraz kilka czujników RF. Kolejno doszły także kamery IP :man_facepalming: po wi-fi :man_facepalming: ale także zapisujące na własnych kartach SD.
Zbudowałem wówczas także swój pierwszy Smogomierz... to były piękne czasy :)

>___ciekawostka:___
>w kamerach znajdują się chińskie karty SD marki "Kingstone" o poj 64GB. Działają - odpukać - niezawodnie od marca/kwietnia 2019 r.

Kolejne zmiany rozpoczęły się od słabej wydajności ówczasnych rozwiązań sieciowych w domu. Po przewertowaniu internetów i youtubów wybór mógł być tylko jeden - Ubiquiti, a dokładniej UniFi. Po przesiadce Wszystkie urządzenia sieciowe zyskały nowe życie, jak również bezpieczeństwo poszło w górę. UniFi Controllera nie nabyłem, więc postanowiłem rozpoznać czym są te "dockery", natomiast szerokopojęte IoT wylądowało na osobnym SSID z odciętym dostępem do internetu (oczywiście z wyjątkami TV, nBoxy itp.). Obok UniFi Controllera w dockerze wylądował także Home Assistant, Node-red i wszystkie inne elementy znajdujące się na SSD-ku. 

Być może przenosiny do "kontenerów", a być może także wysokie wakacyjne temperatury powodowały, że RPi potrafiło się rozgrzać i osiągać nawet 80st! (Na chipach RPi zamontowane były radiatorki, zaś na przestrzałchłodziły je dwa małe wiatraczki). Temperatura i zapewne obciążenie powodowały, że RPi stawało się zawodne i co chwile wieszało.

## Nadszedł czas na NAS :) 

We wrześniu 2019AD zdecydowałem się na zakup QNap'a TS-251B-4GB oraz 2 dysków WD Red o pojemności 1TB. Od razu okazało się, że 4GB to o dużo za mało i zwiększyłem pamięć RAM do 16GB. Niestety nie przemyślałem opcji dysków. Teraz już wiem, że 1TB w RAID to o dużo za mało, ale mam przynajmniej co planować.... Obraz z kamer IP już nie tylko ląduje na kartach SD, ale jest też zapisywany jest na serwerze plików. 

Home Assistant trafił na NASa. Poczatkowo w dockerze. Był to błąd! Ciągłe restarty NASa, Zaweiszanie się HA. Dramat i "myślenice" czy dobrze zrobiłem przesiadając się z RPi. Odłączałem rózne serwisy, nic nie pomagało, a maksymalny uptime nie przekraczał 24h. W chwili desperacji zrezygnowałem z UniFi Controllera w dockerze i zakupiłem Unifi CloudKey.
Po rozmowach ze znajomymi, supportem QNapa i przewertowaniu for internetowych zmieniłem strategię. Porzuciłem dockera na rzecz maszyny wirtualnej. Zmiana inplus była natychmiastowa! Choć nadal występowały problemy, jednak czas ciągłego działąnia dochodził do 5 - 6 dni, a problemy po restarcie ograniczały się tylko do sprawdzenia systemu plików, wcześniej niejednokrotnie musiałem przywracać cały firmware NASa i od nowa tworzyć dockera HomeAssistanta ....

>___ciekawostka:___
>problem niestabilnej pracy QNap'a rozwiązał ostatni update firmware o oznaczeniu 4.4.1.1146 z dnia 06.12.2019r. Od tego czasu system działa stabilnie bez restartów.