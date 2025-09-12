try:
    import usocket as socket
except:
    import socket
import network, time, gc, machine
from machine import Pin, I2C
import dht
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

gc.collect()

# ---------- CONFIG ----------
SSID = 'Robotic WIFI'
PASSWORD = 'rbtWIFI@2025'

# ---------- PINS ----------
LED_PIN   = 2      # D2
DHT_PIN   = 4      # D4
TRIG_PIN  = 27     # D27
ECHO_PIN  = 26     # D26
I2C_SDA   = 21     # D21
I2C_SCL   = 22     # D22

# ---------- HW INIT ----------
led = Pin(LED_PIN, Pin.OUT)
dht_sensor = dht.DHT22(Pin(DHT_PIN))
trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

# LCD init
i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=400000)
addrs = i2c.scan()
lcd_addr = addrs[0] if addrs else 0x27
lcd = I2cLcd(i2c, lcd_addr, 2, 16)

# ---------- WIFI ----------
def connect_wifi(ssid, password, timeout=15):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(ssid, password)
        start = time.time()
        while not wlan.isconnected():
            if time.time() - start > timeout:
                print("WiFi timeout, retry...")
                wlan.disconnect()
                wlan.connect(ssid, password)
                start = time.time()
            time.sleep(0.2)
    print("Connected, ifconfig:", wlan.ifconfig())
    return wlan.ifconfig()[0]

ip = connect_wifi(SSID, PASSWORD)

# ---------- SENSOR HELPERS ----------
def read_dht(retries=3):
    for _ in range(retries):
        try:
            dht_sensor.measure()
            t = dht_sensor.temperature()
            h = dht_sensor.humidity()
            if t is None or h is None:
                raise Exception("DHT returned None")
            return t, h
        except:
            time.sleep(1)
    return None, None

def read_distance(timeout_us=30000):
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    try:
        pulse = machine.time_pulse_us(echo, 1, timeout_us)
        if pulse <= 0:
            return None
        return pulse / 58.0  # µs → cm
    except:
        return None

# ---------- LCD DISPLAY ----------
# Row 1 → Distance, Row 2 → Temperature
def lcd_display(dist=None, temp=None):
    lcd.clear()
    lcd.move_to(0, 0)
    if dist is not None:
        lcd.putstr("Dist:{:.1f}cm".format(dist))
    else:
        lcd.putstr("Dist:N/A")
    lcd.move_to(0, 1)
    if temp is not None:
        lcd.putstr("Temp:{:.1f}C".format(temp))
    else:
        lcd.putstr("Temp:N/A")

# ---------- HTML ----------
def webpage(temp, hum, dist, led_state):
    t_str = f"{temp:.1f}" if temp is not None else "N/A"
    h_str = f"{hum:.1f}" if hum is not None else "N/A"
    d_str = f"{dist:.1f}" if dist is not None else "N/A"
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>ESP32 IoT Webserver</title>
  <meta http-equiv="refresh" content="2">
  <style>
    body{{font-family:Arial; text-align:center; margin-top:30px;}}
    .btn{{padding:10px 20px; margin:8px;}}
    input[type=text]{{padding:8px; width:220px;}}
  </style>
</head>
<body>
  <h1>ESP32 IoT Webserver</h1>
  <h3>LED is {led_state}</h3>
  <a href="/led_on"><button class="btn">LED ON</button></a>
  <a href="/led_off"><button class="btn">LED OFF</button></a>

  <h2>Sensor Readings</h2>
  <p>Temperature: {t_str}&deg;C</p>
  <p>Humidity: {h_str}%</p>
  <p>Distance: {d_str} cm</p>

  <h2>Send to LCD</h2>
  <a href="/show_dist"><button class="btn">Show Distance</button></a>
  <a href="/show_temp"><button class="btn">Show Temp</button></a>
  <a href="/show_both"><button class="btn">Show Both</button></a>

  <h2>Custom LCD Message</h2>
  <form action="/send_text">
    <input type="text" name="msg" placeholder="Enter text">
    <input type="submit" value="Send">
  </form>
  <p style="font-size:0.8em; color:#666;">Auto-refresh every 2s</p>
</body>
</html>
"""
# ---------- SERVER ----------
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
print("Listening on", addr)

def urldecode(s):
    import ure
    s = s.replace('+', ' ')
    hex_pattern = ure.compile(r'%([0-9A-Fa-f]{2})')
    return hex_pattern.sub(lambda m: chr(int(m.group(1), 16)), s)

while True:
    try:
        conn, addr = s.accept()
        request = conn.recv(2048).decode('utf-8', 'ignore')

        # LED control
        if '/led_on' in request:
            led.value(1)
        elif '/led_off' in request:
            led.value(0)

        # Read sensors
        t, h = read_dht()
        d = read_distance()
        led_state = "ON" if led.value() else "OFF"

        # LCD actions
        if '/show_dist' in request:
            lcd_display(dist=d, temp=None)
        elif '/show_temp' in request:
            lcd_display(dist=None, temp=t)
        elif '/show_both' in request:
            lcd_display(dist=d, temp=t)

        # Custom LCD text
        if '/send_text' in request:
            try:
                line = request.split('\n')[0]
                path = line.split(' ')[1]
                if '?' in path:
                    qs = path.split('?', 1)[1]
                    if 'msg=' in qs:
                        val = qs.split('msg=', 1)[1].split('&')[0]
                        val = urldecode(val)
                        lcd.clear()
                        if len(val) <= 16:
                            lcd.putstr(val)
                        else:
                            lcd.putstr(val[:16])
                            lcd.move_to(0, 1)
                            lcd.putstr(val[16:32])
            except Exception as e:
                print("Custom text error:", e)

        # Send webpage
        response = webpage(t, h, d, led_state)
        header = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nConnection: close\r\n\r\n"
        conn.send(header.encode('utf-8'))
        conn.send(response.encode('utf-8'))
        conn.close()

    except Exception as e:
        print("Server error:", e)
        try:
            conn.close()
        except:
            pass
        time.sleep(0.1)