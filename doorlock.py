const submitButton = document.getElementById('submitButton');
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
    LED1=Pin(0,Pin.OUT)
    LED2=Pin(3,Pin.OUT)
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
            servo.duty_u16(7864)
            time.sleep(1)
            servo.duty_u16(3500)
            time.sleep(1)
            speaker.on()
            time.sleep(.5)
            while True:
                LED1.value(1)
                time.sleep(.2)
                LED1.value(0)
                LED2.value(1)
                time.sleep(.2)
                LED2.value(0)
                time.sleep(.1)
            #state = 'ON'
            # while True:
            
            
        elif request == '/motoroff?':
            servo.duty_u16(3500)
            time.sleep(1)
            servo.duty_u16(7864)
            time.sleep(1)
            LED1.value(0)
            LED2.value(0)
            pico_led.off()
            speaker.off()
            time.sleep(.1)
            #state = 'OFF'
            # while True:
            
        temperature = pico_temp_sensor.temp
        html = webpage()
        client.send(html)
        client.close()

try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()