import machine
import network

from umqtt.simple import MQTTClient

NETWORK_CONFIG = {
    "ssid": "",
    "password": "",
}

MQTT_CONFIG = {
    "broker": '192.168.4.1',
    # "client_id": 'esp8266_' + ubinascii.hexlify(machine.unique_id()).decode('utf-8'),
    "client_id": 'p_t_1',
    "topic": 'engine/pressure_transducers',
}

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
        sta_if = network.WLAN(network.STA_IF)

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
        state = 0

        adc = machine.ADC(0)
        self.state = adc.read()

    def next(self):
        return PublishState(self.state)

class PublishState(AbstractState):

    def run(self):
        print("Starting publish...")

        value = str(self.state)

        client = MQTTClient(MQTT_CONFIG['client_id'], MQTT_CONFIG['broker'])
        client.connect()
        client.publish(b'{}/{}/status'.format(MQTT_CONFIG['topic'], MQTT_CONFIG['client_id']), bytes(str(self.state), 'utf-8'))
        client.disconnect()

    def next(self):
        return None
