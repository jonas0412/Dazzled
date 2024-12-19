import network
import espnow
from machine import Pin, PWM
import time
# Motor-Pins
ENABLE_RIGHT_MOTOR = 22
RIGHT_MOTOR_PIN1 = 16
RIGHT_MOTOR_PIN2 = 17
ENABLE_LEFT_MOTOR = 23
LEFT_MOTOR_PIN1 = 18
LEFT_MOTOR_PIN2 = 19
MAX_MOTOR_SPEED = 65535  # Max value for 16-bit PWM
PWM_FREQ = 1000
# Signal-Timeout in Millisekunden
SIGNAL_TIMEOUT = 1000
last_recv_time = time.ticks_ms()
# PWM-Einstellungen
right_motor_pwm = PWM(Pin(ENABLE_RIGHT_MOTOR), freq=PWM_FREQ)
left_motor_pwm = PWM(Pin(ENABLE_LEFT_MOTOR), freq=PWM_FREQ)
right_motor_pin1 = Pin(RIGHT_MOTOR_PIN1, Pin.OUT)
right_motor_pin2 = Pin(RIGHT_MOTOR_PIN2, Pin.OUT)
left_motor_pin1 = Pin(LEFT_MOTOR_PIN1, Pin.OUT)
left_motor_pin2 = Pin(LEFT_MOTOR_PIN2, Pin.OUT)
# ESP-NOW-Initialisierung
wlan = network.WLAN(network.STA_IF)  # Wi-Fi auf Station-Modus setzen
wlan.active(True)
e = espnow.ESPNow()
e.active(True)  # ESP-NOW initialisieren
e.add_peer(b'\xfc\xe8\xc0\x7b\x24\xec')  # Controller MAC-Adresse hinzufügen
# Funktion zur Steuerung der Motoren
def rotate_motor(right_speed, left_speed):
    # Scale speed to 16-bit PWM range
    right_speed = max(0, min(MAX_MOTOR_SPEED, int((right_speed / MAX_MOTOR_SPEED) * 65535)))
    left_speed = max(0, min(MAX_MOTOR_SPEED, int((left_speed / MAX_MOTOR_SPEED) * 65535)))
    # Rechtsmotor
    if right_speed < 0:
        right_motor_pin1.off()
        right_motor_pin2.on()
    elif right_speed > 0:
        right_motor_pin1.on()
        right_motor_pin2.off()
    else:
        right_motor_pin1.off()
        right_motor_pin2.off()
    right_motor_pwm.duty_u16(right_speed)
    # Linksmotor
    if left_speed < 0:
        left_motor_pin1.off()
        left_motor_pin2.on()
    elif left_speed > 0:
        left_motor_pin1.on()
        left_motor_pin2.off()
    else:
        left_motor_pin1.off()
        left_motor_pin2.off()
    left_motor_pwm.duty_u16(left_speed)
# Daten verarbeiten
def process_data(data):
    global last_recv_time
    last_recv_time = time.ticks_ms()
    # Empfange Joystick-Daten
    x_value, y_value, switch_pressed = data
    # Steuerung basierend auf den Werten
    if y_value <= 75:  # Vorwärts
        rotate_motor(MAX_MOTOR_SPEED, MAX_MOTOR_SPEED)
    elif y_value >= 175:  # Rückwärts
        rotate_motor(-MAX_MOTOR_SPEED, -MAX_MOTOR_SPEED)
    elif x_value >= 175:  # Rechts
        rotate_motor(-MAX_MOTOR_SPEED, MAX_MOTOR_SPEED)
    elif x_value <= 75:  # Links
        rotate_motor(MAX_MOTOR_SPEED, -MAX_MOTOR_SPEED)
    else:  # Stop
        rotate_motor(0, 0)
# Hauptloop
while True:
    # Daten empfangen
    host, msg = e.irecv()  # Wartet auf eingehende Daten
    if msg:  # Wenn Daten empfangen wurden
        process_data(msg)
    # Timeout prüfen
    if time.ticks_diff(time.ticks_ms(), last_recv_time) > SIGNAL_TIMEOUT:
        rotate_motor(0, 0)  # Motoren stoppen bei Signalverlust
    time.sleep(0.05)