from machine import ADC
from machine import Pin
from network import STA_IF
from network import WLAN
from umqtt.simple import MQTTClient

NETWORK_CONFIG = {
    "ssid": "",
    "password": "",
}

MQTT_CONFIG = {
    "broker": '192.168.4.1',
    "client_id": 'p_t_1',
    "topic": 'engine/pressure_transducers',
}

# 1 Bar with 3.3v supply
BAR = 220

# Size for sensor measures
WINDOW_SIZE = 20

class AbstractState:
    def __init__(self, state):
        self.state = state

    def run(self):
        raise NotImplementedError("run method must be implemented")

    def next(self):
        raise NotImplementedError("next method must be implemented")


class ConnectState(AbstractState):
    def run(self):
        print("Starting connect...")
        sta_if = WLAN(STA_IF)

        if not sta_if.isconnected():
            print('connecting to network...')
            sta_if.active(True)
            sta_if.connect(NETWORK_CONFIG['ssid'], NETWORK_CONFIG['password'])

            while not sta_if.isconnected():
                pass

            print("Connected!")
            self.state = 1
        else:
            self.state = 1

        return self.state

    def next(self):
        return MeasureState(self.state) if self.state == 1 else self

class MeasureState(AbstractState):
    def run(self):
        print("Starting measure...")

        # Create ADC object on pin 32
        adc = ADC(Pin(34, Pin.IN))

        # set 11dB input attentuation (voltage range roughly 0.0v - 3.6v)
        adc.atten(ADC.ATTN_11DB)

        # read voltage
        voltage = self.__read_median_voltage(adc, WINDOW_SIZE)

        # calc bars
        self.state = voltage / BAR

    def next(self):
        return PublishState(self.state)

    def __read_median_voltage(self, adc, window_size):
        measures = []

        while len(measures) < window_size:
            measures.append(adc.read())

        measures.sort()

        if self.__even(window_size):
            mid = window_size / 2
            return (measures[mid] + measures[mid+1]) / 2
        else:
            mid = int(window_size / 2) + 1
            return measures[mid]

    def __even(self, n):
        n % 2 == 0

class PublishState(AbstractState):

    def run(self):
        value = str(self.state)

        print("Proceding to publish value: " + value)

        client = MQTTClient(MQTT_CONFIG['client_id'], MQTT_CONFIG['broker'])
        client.connect()
        client.publish(b'{}/{}/status'.format(MQTT_CONFIG['topic'], MQTT_CONFIG['client_id']), bytes('%.2f'%(self.state), 'utf-8'))
        client.disconnect()

    def next(self):
        return None
