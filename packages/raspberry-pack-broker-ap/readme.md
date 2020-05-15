Creates an access point and MQTT broker

## Access Point Configuration (AP) 
 - Adjust `hostapd.conf` to setup how your Wi-Fi is named (`ssid`) and secured (`wpa_passphrase`)
 - Adjust `dnsmasq.conf` to setup your AP's IP-range (`listen-address` and `dhcp-range`)

# MQTT Broker Configuration
 - Adjust `mosquitto.conf` to your needs (`mosquitto.conf`), 
 - Port `1883` and `9001` are active by default