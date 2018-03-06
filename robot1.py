# coding: utf-8

import ui
import math

from utils import Config
from tpp import ipc

CONFIG_PATH = '.drive.config'
config = Config.load(CONFIG_PATH)

class RobotCommand(object):

    def __init__(self):
        self.cli = None
        self.on_close = None

    def start(self, ip_address, portnum):
        self.cli = ipc.SimpleClient((ip_address, portnum), ipc.JSONPacker())
        self.cli.start()

    def stop(self):
        self.cli.close()
        if self.on_close:
            self.on_cloase()

    def _send(self, msg):
        self.cli.send(msg)
        return self.cli.recv()[0] == 'success'

    def enable(self):
        return self._send(['enable'])

    def duty(self, a_duty, b_duty):
        self._send(['duty', a_duty, b_duty])

class ControlPad(ui.View):
    def __init__(self):
        self.vector = lambda x,y:None
        self.center_x = 150.0 #self.bounds[2]/2
        self.center_y = 150.0 #self.bounds[3]/2
        self.half_width = self.center_x
        self.move_threashold = 0.1
        self.set_needs_display()

    def draw(self):
        path = ui.Path()
        path.line_width = 1
        path.line_join_style = ui.LINE_JOIN_ROUND
        path.line_cap_style = ui.LINE_CAP_ROUND
        path.move_to(self.center_x, 0)
        path.line_to(self.center_x, self.center_y*2)
        path.stroke()
        path.move_to(0, self.center_y)
        path.line_to(self.center_x*2, self.center_y)
        path.stroke()

    def touch_began(self, touch):
        x, y = touch.location
        self.xy = ((x - self.center_x)/self.half_width,
        (self.center_y - y)/self.half_width)
        self.vector(self.xy)

class RobotController(object):
    def __init__(self, topv):
        self._robot = RobotCommand()
        
        topv.background_color = '#2f2f2f'

        v_ipaddress = topv['IP_address']
        v_ipaddress.action = self.enter_ipaddress
        if config.ip_address:
            v_ipaddress.text = config.ip_address

        v_button_connect = topv['connect']
        v_button_connect.action = self.do_connect

        v_control_pad = topv['control_pad']
        v_control_pad.vector = self._vector
        
        self.v_A_ratio = topv['A_ratio']
        self.v_B_ratio = topv['B_ratio']

    def _vector(self, xy):
        x, y = xy
        r = math.sqrt(x**2 + y**2)
        if r > 1.0:
            y /= r
            r = 1.0
        if y > 0 and x > 0:
            left, right = r, y
        elif y > 0 and x < 0:
            left, right = y, r
        elif y < 0 and x < 0:
            left, right = y, -r
        elif y < 0 and x > 0:
            left, right = -r, y
        else:
            left, right = 0, 0
        left = round(left, 1)
        right = round(right, 1)
        self.v_A_ratio.text = '%2.1f' % left
        self.v_B_ratio.text = '%2.1f' % right
        self._robot.duty(right, left)

    def enter_ipaddress(self, sender):
        self.v_message.text = sender.text
        config.ip_address = sender.text
        config.save()

    def do_connect(self, sender):
        self._robot.start(config.ip_address, 2001)
        if self._robot.enable():
            sender.enabled = False


v = ui.load_view('robot1-ipad')
robot_controller = RobotController(v)
v.present('sheet')

