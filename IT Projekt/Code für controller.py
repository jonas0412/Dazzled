import network
import espnow
from machine import Pin, ADC
import time

# Konfiguration der Pins
X_AXIS_PIN = 32
Y_AXIS_PIN = 33
SWITCH_PIN = 25

# Empfänger MAC-Adresse
RECEIVER_MAC = b'\xcc\xdb\xa7\x2d\xa5\x0c'  # MAC-Adresse des Autos

# Initialisiere ADCs für den Joystick
x_axis_adc = ADC(Pin(X_AXIS_PIN))
x_axis_adc.atten(ADC.ATTN_11DB)
x_axis_adc.width(ADC.WIDTH_12BIT)

y_axis_adc = ADC(Pin(Y_AXIS_PIN))
y_axis_adc.atten(ADC.ATTN_11DB)
y_axis_adc.width(ADC.WIDTH_12BIT)

# Konfiguration der Taste
switch = Pin(SWITCH_PIN, Pin.IN, Pin.PULL_UP)

# Joystick-Werte auf 0-254 skalieren und Deadband anpassen
def map_and_adjust_joystick(value, reverse=False):
    if value >= 2200:
        mapped_value = int((value - 2200) * (254 - 127) / (4095 - 2200) + 127)
    elif value <= 1800:
        mapped_value = int((value - 1800) * (0 - 127) / (0 - 1800) + 127)
    else:
        mapped_value = 127

    if reverse:
        mapped_value = 254 - mapped_value
    return mapped_value

# Initialisierung von ESP-NOW
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

e = espnow.ESPNow()
e.active(True)
e.add_peer(RECEIVER_MAC)

# Hauptloop
while True:
    x_value = map_and_adjust_joystick(x_axis_adc.read())
    y_value = map_and_adjust_joystick(y_axis_adc.read())
    switch_pressed = 0 if switch.value() else 1

    # Datenpaket senden
    data = bytes([x_value, y_value, switch_pressed])
    e.send(RECEIVER_MAC, data)

    # Verzögerung, wenn der Schalter gedrückt ist
    time.sleep(0.5 if switch_pressed else 0.05)

