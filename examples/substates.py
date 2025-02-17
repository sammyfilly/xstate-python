#!/usr/bin/env python3

# add parent to the path to include local xstate module
import sys

sys.path.insert(0, "..")

import time  # noqa

from xstate import Machine  # noqa

# Trafic light example with substate
# green -> yellow -> red.walk -> red.wait -> red.stop -> green ..

lights = Machine(
    {
        "id": "lights",
        "initial": "green",
        "states": {
            "green": {
                "entry": [{"type": "enterGreen"}],
                "on": {"TIMER": "yellow"},
            },
            "yellow": {"on": {"TIMER": "red"}},
            "red": {  # subFSM
                "initial": "walk",
                "states": {
                    "walk": {"on": {"COUNTDOWN": "wait"}},
                    "wait": {"on": {"COUNTDOWN": "stop"}},
                    "stop": {"on": {"TIMEOUT": "timeout"}},
                    "timeout": {"type": "final"},
                    # type 'final' will make it to the onDone step of the superior FSM
                },
                "onDone": "green",
            },
        },
    }
)

if __name__ == "__main__":
    state = lights.initial_state
    print(state.value)
    time.sleep(0.5)

    for _ in range(10):
        state = lights.transition(state, "TIMER")
        print(state.value)
        time.sleep(0.5)

        state = lights.transition(state, "TIMER")
        print(state.value)
        time.sleep(0.5)

        state = lights.transition(state, "COUNTDOWN")
        print(state.value)
        time.sleep(0.5)

        state = lights.transition(state, "COUNTDOWN")
        print(state.value)
        time.sleep(0.5)

        state = lights.transition(state, "TIMEOUT")
        print(state.value)
        time.sleep(0.5)
