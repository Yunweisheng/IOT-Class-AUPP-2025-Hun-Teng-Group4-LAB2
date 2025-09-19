# LAB2: IoT Webserver with LED, Sensors, and LCD Control

## 1) Overview
ESP32 + MicroPython project with a browser-based UI to:
- Toggle an **LED**
- Read **DHT11** (temperature/humidity) + **HC-SR04** (distance)
- Show selected sensor values on a **16×2 I²C LCD**
- Send **custom text** from the webpage to the LCD

Focus: event-driven interaction between web UI and hardware.

---

## 2) Learning Outcomes
- Build a MicroPython **webserver** with HTML controls
- Control an **LED** from the browser
- Read **DHT11** + **ultrasonic** and show on a webpage
- Send sensor values to **LCD** via buttons
- Send **custom text** (textbox → LCD)
- Document wiring and usage clearly

---

## 3) Equipment
- ESP32 Dev Board (with MicroPython)
- DHT11 sensor
- HC-SR04 ultrasonic sensor
- 16×2 LCD with **I²C** backpack
- Breadboard, jumper wires, USB cable
- Laptop with **Thonny**
- Wi-Fi access

---
## 4) Wiring
