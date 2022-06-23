import logging

logger = logging.getLogger(__name__)

class SnifferState(object):
    name = "state"
    prev_state = "prev_state"
    allowed = []

    def switch_state(self, state):
        """ Switch to new state """
        if state.name in self.allowed:
            if self.prev_state != state.name:
                logger.info(f"Current state: '{self}' switched to '{state.name}'")
                self.prev_state = state.name
                self.__class__ = state
        else:
            logger.info(f"Current state: '{self}' switching to '{state.name}' not possible!.")

    def __str__(self):
        return self.name


class Boot(SnifferState):
    name = "boot"
    allowed = ['ready_to_sniff', 'not_mounted', 'error']


class NotMounted(SnifferState):
    name = "not_mounted"
    allowed = ['ready_to_sniff', 'error']


class Ready(SnifferState):
    """ State of being successfully started up and waiting for start button to get pressed """

    name = "ready_to_sniff"
    allowed = ['ready_to_sniff', 'start_sniffing', 'error', 'not_mounted']


class StartSniffing(SnifferState):
    """ State of preparing for sniffing. Sniffle process and monitoring should
    successfully be started and setted up. """

    name = "start_sniffing"
    allowed = ['sniffing', 'error']


class Sniffing(SnifferState):
    """ State of beeing actively sniffing. Sniffle process is actively monitored.
    As long as sniffle pid is active running, this state does not change. """

    name = "sniffing"
    allowed = ['stop_sniffing', 'error']


class StopSniffing(SnifferState):
    """ State of being in suspended mode after switched on """

    name = "stop_sniffing"
    allowed = ['ready_to_sniff', 'error']

class Error(SnifferState):
    """ State of being in suspended mode after switched on """

    name = "error"
    allowed = ['error', 'ready_to_sniff', 'not_mounted']


class Sniffer(object):
    """ A class representing a sniffer """

    def __init__(self, model='Sniffer'):
        self.model = model
        # State of the sniffer - default is Boot.
        self.state = Boot()

    def change_state_to(self, state):
        """ Change state """
        self.state.switch_state(state)

    def get_state(self):
        """ Get state """
        return self.state.name