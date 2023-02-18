import time
import json
import socket
import pyautogui
import base64
from PIL import Image, ImageGrab, ImageDraw
from io import BytesIO


class Client:
	def __init__(self, ip, port):
		self.ip = ip
		self.port = port
		self.command = ""

		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		while True:
			try:
				self.client.connect((self.ip, self.port))
				print("connected")
				break
			except:
				time.sleep(5)

		self.send_json("connected")

	def execute_commands(self):
		while True:
			command = self.recieve_json()
			result = self.get_screenshot()
			if command[0] == "move":
				result = self.move_mouse(int(command[1]), int(command[2]))
			if command[0] == "mouse_click":
				result = self.mouse_click(int(command[1]))
			self.send_json(result)

	def get_screenshot(self):
		custom_buffer = BytesIO()

		screen = ImageGrab.grab()
		pencil = ImageDraw.Draw(screen)
		mouse_x, mouse_y = pyautogui.position()
		pencil.rectangle((mouse_x - 5, mouse_y - 5, mouse_x + 5, mouse_y + 5), fill="red")
		screen.save(custom_buffer, "jpeg")
		screen_code = base64.b64encode(custom_buffer.getvalue())

		return screen_code

	def recieve_json(self):
		json_data = ""
		while True:
			try:
				json_data += self.client.recv(1024).decode("utf-8")
				return json.loads(json_data)
			except ValueError:
				pass

	def send_json(self, data):
		try:
			json_data = json.dumps(data.decode("utf-8"))
		except:
			json_data = json.dumps(data)
			
		self.client.send(json_data.encode("utf-8"))

	def move_mouse(self, x: int, y: int):
		pyautogui.move(x, y)
		return ["move:", str(x), str(y)]

	def mouse_click(self, flag: int):
		if flag == 1:
			pyautogui.leftClick()
			return ["left_click:", str(pyautogui.position()[0]), str(pyautogui.position()[1])]
		if flag == 2:
			pyautogui.rightClick()
			return ["right_click:", str(pyautogui.position()[0]), str(pyautogui.position()[1])]

client = Client("192.168.1.76", 5050)
client.execute_commands()