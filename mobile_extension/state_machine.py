class SnifferState(object):
    name = "state"
    allowed = []

    def switch_state(self, state):
        """ Switch to new state """
        if state.name in self.allowed:
            print('Current state:', self, ' => switched to new state', state.name)
            self.__class__ = state
        else:
            print('Current state:', self, ' => switching to', state.name, 'not possible.')

    def __str__(self):
        return self.name


class Boot(SnifferState):
    name = "boot"
    allowed = ['ready_to_sniff', 'not_mounted']


class NotMounted(SnifferState):
    name = "not_mounted"
    allowed = ['ready_to_sniff']


class Ready(SnifferState):
    """ State of being successfully started up and waiting for start button to get pressed """

    name = "ready_to_sniff"
    allowed = ['off', 'start_sniffing']


class StartSniffing(SnifferState):
    """ State of preparing for sniffing. Sniffle process and monitoring should
    successfully be started and setted up. """

    name = "start_sniffing"
    allowed = ['off', 'sniffing']


class Sniffing(SnifferState):
    """ State of beeing actively sniffing. Sniffle process is actively monitored.
    As long as sniffle pid is active running, this state does not change. """

    name = "sniffing"
    allowed = ['off', 'stop_sniffing']


class StopSniffing(SnifferState):
    """ State of being in suspended mode after switched on """

    name = "stop_sniffing"
    allowed = ['off', 'ready_to_sniff']


class Sniffer(object):
    """ A class representing a sniffer """

    def __init__(self, model='HP'):
        self.model = model
        # State of the computer - default is off.
        self.state = NotMounted()

    def change_state(self, state):
        """ Change state """
        self.state.switch_state(state)


if __name__ == "__main__":
    sniffer = Sniffer()
    sniffer.change_state(Boot)
    sniffer.change_state(Ready)
    sniffer.change_state(NotMounted)
    sniffer.change_state(Ready)
    sniffer.change_state(StartSniffing)
    sniffer.change_state(Sniffing)
    sniffer.change_state(StopSniffing)
    sniffer.change_state(Ready)