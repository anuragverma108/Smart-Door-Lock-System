import network
import socket
import time
from picozero import pico_temp_sensor, pico_led, Speaker
from machine import Pin, PWM

ssid = 'EDITH'
password = 'Deadshot'

def connect():
    # Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        print('Waiting for connection...')
        time.sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def webpage(temperature, state):
    # Template HTML
    html = """
    <!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Smart Door Lock System</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: linear-gradient(45deg, #ff9a9e, #fad0c4, #ffecd9, #d1f2eb, #a6eddd);
      background-size: 400% 400%;
      animation: gradientAnimation 15s ease infinite;
      color: #333;
      margin: 0;
      padding: 0;
    }

    @keyframes gradientAnimation {
      0% {
        background-position: 0% 50%;
      }
      50% {
        background-position: 100% 50%;
      }
      100% {
        background-position: 0% 50%;
      }
    }

    .container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
      position: relative;
      z-index: 2;
    }

    .door-wrapper {
      position: relative;
      margin-bottom: 20px;
    }

    .door-container {
      width: 300px;
      height: 400px;
      perspective: 1000px;
      position: relative;
      z-index: 1;
      transform-origin: left center;
      transition: transform 1s ease-in-out;
    }

    .door-container.open {
      transform: scale(0.8);
    }

    .door {
      width: 100%;
      height: 100%;
      position: relative;
      transform-style: preserve-3d;
      transform-origin: left center;
      background-color: #f2c94c;
      box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
    }

    .door-handle {
      width: 30px;
      height: 10px;
      background-color: #333;
      position: absolute;
      top: 50%;
      right: 20px;
      transform: translateY(-50%);
    }

    .input-container {
      margin-top: 20px;
    }

    #messageContainer {
      margin-top: 20px;
      text-align: center;
    }

    @keyframes openDoor {
      0% {
        transform: rotateY(0deg);
      }
      100% {
        transform: rotateY(-45deg);
      }
    }

    @keyframes closeDoor {
      0% {
        transform: rotateY(-45deg);
      }
      100% {
        transform: rotateY(0deg);
      }
    }
  </style>
   </head>
   <body>
  <div class="container">
    <h1>Welcome to our Smart Door Lock System</h1>
    <div class="door-wrapper">
      <div class="door-container">
        <div class="door">
          <div class="door-handle"></div>
        </div>
      </div>
    </div>
    <form id="openDoorForm">
      <div class="input-container">
        <input type="password" id="passwordInput" placeholder="Enter Password" required>
        <button type="submit" id="submitButton">Open Door</button>
      </div>
    </form>
    <form id="closeDoorForm">
      <button type="submit" id="closeButton">Lock Door</button>
    </form>
    <div id="messageContainer"></div>
  </div>

  <script>
    const doorElement = document.querySelector('.door');
    const doorContainer = document.querySelector('.door-container');
    const openDoorForm = document.getElementById('openDoorForm');
    const closeDoorForm = document.getElementById('closeDoorForm');
    const passwordInput = document.getElementById('passwordInput');const submitButton = document.getElementById('submitButton');
    const closeButton = document.getElementById('closeButton');
    const messageContainer = document.getElementById('messageContainer');
    const correctPassword = 'opendoor';
    window.history.pushState({}, '', './motoroff');
    openDoorForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const enteredPassword = passwordInput.value;
      if (enteredPassword === correctPassword) {
        doorElement.style.animation = 'openDoor 1s ease-in-out forwards';
        doorContainer.classList.add('open');
        setTimeout(() => {
          messageContainer.innerHTML = '<p style="color: #2ecc71;">Welcome Home!</p>';
          openDoorForm.style.display = 'none';
          closeDoorForm.style.display = 'block';
          const motorOnEvent = new CustomEvent('motorOn');
          window.dispatchEvent(motorOnEvent);
          openDoorForm.submit();
        }, 1000);
      } else {
        messageContainer.innerHTML = '<p style="color: #e74c3c;">Wrong password. Please try again.</p>';
      }
      passwordInput.value = '';
    });
    closeDoorForm.addEventListener('submit', (event) => {
      event.preventDefault();
      doorElement.style.animation = 'closeDoor 1s ease-in-out forwards';
      doorContainer.classList.remove('open');
      setTimeout(() => {
        messageContainer.innerHTML = '';
        openDoorForm.style.display = 'block';
        closeDoorForm.style.display = 'none';
        const motorOffEvent = new CustomEvent('motorOff');
        window.dispatchEvent(motorOffEvent);
      }, 1000);
    closeDoorForm.submit();
    });
    window.addEventListener('motorOn', () => {
      window.history.pushState({}, '', './motoron');
    });
    window.addEventListener('motorOff', () => {
      window.history.pushState({}, '', './motoroff');
    });
  </script>
   </body>
   </html>
    """
    return str(html)

def serve(connection):
    # Start a web server
    state = 'OFF'
    servo = PWM(Pin(8, mode=Pin.OUT))
    servo.freq(50)
    speaker = Speaker(15)
   
    LED=Pin(0,Pin.OUT)
    temperature = 0
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request == '/motoron?':
            LED.value(1)
            speaker.on()
            time.sleep(1)
            state = 'ON'
            # while True:
            servo.duty_u16(7864)
            time.sleep(1)
            servo.duty_u16(3500)
            time.sleep(1)
            
        elif request == '/motoroff?':
            LED.value(0)
            pico_led.off()
            speaker.off()
            time.sleep(1)
            state = 'OFF'
            # while True:
            servo.duty_u16(3500)
            time.sleep(1)
            servo.duty_u16(7864)
            time.sleep(1)
        temperature = pico_temp_sensor.temp
        html = webpage(temperature, state)
        client.send(html)
        client.close()

try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()