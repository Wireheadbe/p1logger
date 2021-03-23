# p1logger
## Prerequisites
* A P1 cable - I got mine from https://www.bol.com/nl/p/slimme-meter-kabel-p1-usb/9200000111535827/?s2a= (not affiliated)
## Set-Up
* Install python paho mqtt client
* Define 3 variables in the script (broker / port / p1device)
* Included is a .service file, to run the script at boottime via systemd in a screen session (do change paths :) )
