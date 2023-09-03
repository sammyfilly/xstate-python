#!/usr/bin/env python3

import time

from xstate import Machine

# Trafic light example
# green -> yellow -> red -> green ..
timing = 2


def enterGreen():
    print("\tENTER_GREEN callback")


def exitGreen():
    print("\tEXIT_GREEN callback")


# fmt: off
lights = Machine(
    {
        "id": "lights",
        "initial": "green",
        "states": {
            "green": {
                "on": {"TIMER": "yellow"},
                "entry": [{"type": "enterGreen"}],
                "exit": [{"type": "exitGreen"}],
            },
            "yellow": {
                "on": {"TIMER": "red"},
                "entry": [{"type": "enterYellow"}]
            },
            "red": {
                "on": {"TIMER": "green"},
                "entry": [lambda: print("\tINLINE callback")],
            },
        },
    },
    actions={
        # action implementations
        "enterGreen": enterGreen,
        "exitGreen": exitGreen,
        "enterYellow": lambda: print("\tENTER_YELLOW callback"),
    },
)
# fmt: on

if __name__ == "__main__":
    state = lights.initial_state

    for _ in range(10):
        # execute all the actions (before/exit states)
        for action in state.actions:
            action()
        print(f"VALUE: {state.value}")

        time.sleep(timing)
        state = lights.transition(state, "TIMER")
