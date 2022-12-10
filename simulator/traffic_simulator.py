from argparse import ArgumentParser
from random import choices
import paho.mqtt.client as mqtt
import time
import yaml
import config

STATES = {}

def parse_args():
    parser = ArgumentParser('Parse parameters to determine possible traffic')
    group = parser.add_mutually_exclusive_group(required=False)
    parser.add_argument(
            'season',
            choices=['autumn', 'winter', 'spring', 'summer', 'default'],
            help='Season of the year',
            default='default',
            nargs='?',
            type=str
            )
    parser.add_argument(
            'daytime',
            choices=['morning', 'dusk', 'evening', 'night', 'default'],
            help='Time of the day',
            default='default',
            nargs='?',
            type=str
            )
    parser.add_argument(
            'weather',
            choices=['windy', 'rainy', 'snowy', 'cloudy', 'default'],
            help='Present weather',
            default='default',
            nargs='?',
            type=str
            )
    group.add_argument(
            '--best',
            help='Best possible conditions',
            action='store_true'
            )
    group.add_argument(
            '--worst',
            help='Worst possible conditions',
            action='store_true'
            )
    return parser.parse_args()

def load_conditions():
    with open(config.WEIGHTS_FILE, 'r') as weights_file:
        try:
            return yaml.safe_load(weights_file)
        except YAMLError as error:
            print(error)

def determine_weight(args, conditions):
    weight = 0
    if args.worst:
        return len(conditions)
    elif args.best:
        return 5*len(conditions)
    else:
        for condition in conditions:
            weight += conditions[condition][eval(f'args.{condition}')]
    return weight

def update_states(STATES, sensor, choice):
    if sensor not in STATES:
        STATES[sensor] = choice
        STATES[f'current{sensor}'] = choice
    else:
        STATES[sensor] += choice
        STATES[f'current{sensor}'] = choice
    return STATES

def display_states(STATES):
    print('\033[92m' + 50*'-' + '\n')
    for i in range(config.NUMBER_OF_SENSORS):
        print('\033[91m' +
                f'Current state of sensor number {i}: ' +
                str(STATES[f'current{i}']) +
                '\033[0m')
        print('\033[91m' +
                f'Sum of pedestrians detected by sensor number {i}: ' +
                str(STATES[i]) +
                '\033[0m')
        print(10*'-')
    print('\n')

def start_simulator(client, conditions, weight, STATES):
    tmp = weight
    while True:
        for i in range(config.NUMBER_OF_SENSORS):
            if i in config.DESOLATED_SENSORS:
                weight /= 2
            choice = choices([1, 0],
                    weights = [(weight/(2*3*len(conditions))),
                    1 - (weight/(3*2*len(conditions)))])[0]
            STATES = update_states(STATES, i, choice)
            client.publish(f"{config.SIMULATOR_SENSORS_PATTERN}{i}", choice)
            weight = tmp
        display_states(STATES)
        time.sleep(config.SIMULATOR_POLLING_RATE)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("executor/sensors_group/+")

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

def main():
    args = parse_args()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(
            config.MQTT_ADDRESS,
            config.MQTT_PORT,
            config.MQTT_TIMEOUT
            )

    conditions = load_conditions()
    weight = determine_weight(args, conditions)
    start_simulator(client,conditions, weight, STATES)

if __name__ == "__main__":
    main()
