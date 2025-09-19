LAB2: IoT Webserver with LED, Sensors, and LCD Control
1) Overview

Build an ESP32-based IoT system with MicroPython that:

Serves a web page to control an LED

Reads DHT11 (temperature/humidity) and HC-SR04 (ultrasonic distance)

Shows selected sensor values on a 16×2 LCD (I²C)

Displays custom text from a webpage textbox on the LCD

This lab focuses on event-driven interaction between a web UI and hardware.

2) Learning Outcomes

By the end, you can:

Implement a MicroPython webserver with HTML controls

Toggle an LED from the browser

Read DHT11 + ultrasonic and publish values on the web page

Send sensor values to an LCD via buttons

Send custom text from a textbox to the LCD

Document wiring and usage
