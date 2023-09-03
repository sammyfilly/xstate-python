from typing import TYPE_CHECKING, Dict, List, Optional, Union

from xstate.action import Action
from xstate.transition import Transition

if TYPE_CHECKING:
    from xstate.machine import Machine


class StateNode:
    on: Dict[str, List[Transition]]
    machine: "Machine"
    parent: Optional["StateNode"]
    initial: Optional[Transition]
    entry: List[Action]
    exit: List[Action]
    donedata: Optional[Dict]
    type: str  # 'atomic' or 'compound' or 'parallel' or 'final'
    transitions: List[Transition]
    id: str
    key: str
    states: Dict[str, "StateNode"]

    def get_actions(self, action):
        if callable(action):
            return Action(action)
        else:
            return Action(action.get("type"), exec=None, data=action)

    def __init__(
        self,
        # { "type": "compound", "states": { ... } }
        config,
        machine: "Machine",
        key: str,
        parent: Union["StateNode", "Machine"] = None,
    ):
        self.config = config
        self.parent = parent
        self.id = (
            config.get("id", f"{parent.id}.{key}")
            if parent
            else config.get("id", f"{machine.id}.{key}")
        )
        self.entry = (
            [self.get_actions(entry_action) for entry_action in config.get("entry")]
            if config.get("entry")
            else []
        )

        self.exit = (
            [self.get_actions(exit_action) for exit_action in config.get("exit")]
            if config.get("exit")
            else []
        )

        self.key = key
        self.states = {
            k: StateNode(v, machine=machine, parent=self, key=k)
            for k, v in config.get("states", {}).items()
        }
        self.on = {}
        self.transitions = []
        for k, v in config.get("on", {}).items():
            self.on[k] = []
            transition_configs = v if isinstance(v, list) else [v]

            for transition_config in transition_configs:
                transition = Transition(
                    transition_config,
                    source=self,
                    event=k,
                    order=len(self.transitions),
                )
                self.on[k].append(transition)
                self.transitions.append(transition)

        self.type = config.get("type")

        if self.type is None:
            self.type = "atomic" if not self.states else "compound"

        if self.type == "final":
            self.donedata = config.get("data")

        if config.get("onDone"):
            done_event = f"done.state.{self.id}"
            done_transition = Transition(
                config.get("onDone"),
                source=self,
                event=done_event,
                order=len(self.transitions),
            )
            self.on[done_event] = done_transition
            self.transitions.append(done_transition)

        machine._register(self)

    @property
    def initial(self):
        if initial_key := self.config.get("initial"):
            return Transition(
                self.states.get(initial_key), source=self, event=None, order=-1
            )
        if self.type == "compound":
            return Transition(
                next(iter(self.states.values())), source=self, event=None, order=-1
            )

    def _get_relative(self, target: str) -> "StateNode":
        if target.startswith("#"):
            return self.machine._get_by_id(target[1:])

        if state_node := self.parent.states.get(target):
            return state_node
        else:
            raise ValueError(
                f"Relative state node '{target}' does not exist on state node '#{self.id}'"  # noqa
            )

    def __repr__(self) -> str:
        return "<StateNode %s>" % repr({"id": self.id})
