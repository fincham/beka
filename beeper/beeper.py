from beeper.event import Event
from beeper.bgp_message import BgpMessage, BgpOpenMessage, BgpKeepaliveMessage
from beeper.ip4 import ip_number_to_string, ip_string_to_number
from collections import deque

import time

class Beeper:
    DEFAULT_HOLD_TIME = 60
    DEFAULT_KEEPALIVE_TIME = DEFAULT_HOLD_TIME // 3

    def __init__(self, my_as, peer_as, my_id, peer_id, hold_time):
        self.my_as = my_as
        self.peer_as = peer_as
        self.my_id = my_id
        self.peer_id = peer_id
        self.hold_time = hold_time
        self.keepalive_time = hold_time // 3
        self.output_messages = deque()

        tick = int(time.time())

        self.timers = {
            "hold": tick + self.hold_time,
            "keepalive": tick + self.keepalive_time,
        }
        self.state = "active"

    def event(self, event):
        if event.type == Event.TIMER_EXPIRED:
            self.handle_timers(event.epoch)
        elif event.type == Event.MESSAGE_RECEIVED:
            self.handle_message(event.message)

    def handle_timers(self, epoch):
        if self.timers["hold"] <= epoch:
            self.handle_hold_timer(epoch)

        if self.timers["keepalive"] <= epoch:
            self.handle_keepalive_timer(epoch)

    def handle_hold_timer(self, epoch):
        # do stuff
        # should be state check too
        self.state = "active"

    def handle_keepalive_timer(self, epoch):
        # do stuff
        self.timers["keepalive"] = epoch + self.keepalive_time
        message = BgpKeepaliveMessage()
        self.output_messages.append(message)

    def handle_message(self, message):# state machine
        if self.state == "active":
            if message.type == BgpMessage.OPEN_MESSAGE:
                # TODO sanity check incoming open message
                open_message = BgpOpenMessage(4, self.my_as, self.hold_time, ip_string_to_number(self.my_id))
                keepalive_message = BgpKeepaliveMessage()
                self.output_messages.append(open_message)
                self.output_messages.append(keepalive_message)
                self.state = "open_confirm"
        elif self.state == "open_confirm":
            if message.type == BgpMessage.KEEPALIVE_MESSAGE:
                self.state = "established"

