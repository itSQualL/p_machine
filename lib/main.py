import machine

from p_machine.p_machine import PMachine
from p_machine.states import ConnectState

def do_deep_sleep():
    # put the device to sleep
    print("Machine sleeping now...")
    machine.deepsleep(20000)

def run_machine():
    try:
        print("Running machine...")
        return PMachine(ConnectState(0)).run()
    except Exception as e:
        print(str(e))
        return False

def main():
    print("Starting...")
    finished = False

    while not finished:
        finished = run_machine()

    do_deep_sleep()


if __name__ == '__main__':
    main()
