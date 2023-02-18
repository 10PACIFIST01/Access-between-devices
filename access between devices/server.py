from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image as WidgetImage
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock


from io import BytesIO
import json
import socket
import threading
import base64


class Thread:
	def __init__(self, ip, port):
		self.ip = ip
		self.port = port
		self.command = "command"

		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server.bind((self.ip, self.port))
		self.server.listen(0)
		self.responce = ""
		self.cursor_speed = 50
		self.stop_flag = False
		self.button_pressed = False

		self.buff = BytesIO()

	def run(self):
		self.active, self.address = self.server.accept()

		while self.active:
			self.responce = self.recieve_json()
			self.update_buffer(self.responce)

			self.send_json(self.command)
			if not self.button_pressed:
				self.command = "command"

			if self.stop_flag:
				break

	def send_json(self, data):
		json_data = json.dumps(data)
		self.active.send(json_data.encode("utf-8"))

	def recieve_json(self):
		json_data = ""
		while True:
			try:
				if self.active != None:
					json_data += self.active.recv(1024).decode("utf-8")
					return json.loads(json_data)
				else:
					return None
			except ValueError:
				pass

	def update_buffer(self, screen):
		try:
			decoded_image = self.decode_screenshot(screen)
			self.buff = BytesIO()
			self.buff.write(decoded_image)
			self.buff.seek(0)
		except:
			pass

	def decode_screenshot(self, screen):
		return base64.b64decode(screen)


class MainDisplay(BoxLayout):
	pass


class ServerApp(App):
	def set_screenshot(self, dt):
		buff = self.server.buff

		#buff = BytesIO(open("screen.jpg", "rb").read())
		buff.seek(0)

		try:
			beeld = CoreImage(BytesIO(buff.read()), ext="jpg")
			self.image_layout.texture = beeld.texture
			self.label.text = f"{len(buff.getvalue())}"
			print("Image has been downloaded successfully")
		except:
			print("error")

	def __init__(self):
		super().__init__()

		self.server = Thread("192.168.1.66", 5050)
		self.runner = threading.Thread(target = self.server.run)
		self.runner.start()

		self.image_layout = WidgetImage(allow_stretch = True, keep_ratio = False, size_hint = [1, 1])

		print(self.server.buff)

		Clock.schedule_interval(self.set_screenshot, 1 / 5)


	def build(self):

		self.label = Label(text = "label text",
			size_hint = [1, .3],
			outline_color = (.3, .3, .3, 1),
			text_size = (100, 50),
			valign = "top")

		self.box_layout = BoxLayout(orientation = "vertical")
		#self.image_layout = WidgetImage()

		top_button_layout = AnchorLayout(anchor_x = "center", anchor_y = "bottom", size_hint = [1, .2])
		middle_buttons_layout = BoxLayout(orientation = "horizontal", size_hint = [1, .2])
		bottom_button_layout = AnchorLayout(anchor_x = "center", anchor_y = "top", size_hint = [1, .2])

		self.box_layout.add_widget( self.label )
		top_button_layout.add_widget( Button(text = "/\\",
			size_hint = (.7, .3),
			halign = "center",
			valign = "bottom",
			on_press = self.mouse_move,
			on_release = self.mouse_release) )
		middle_buttons_layout.add_widget( Button(text = "<", on_press = self.mouse_move, on_release = self.mouse_release) )
		middle_buttons_layout.add_widget( Button(text = "LEFT", on_press = self.mouse_click) )
		middle_buttons_layout.add_widget( Button(text = "RIGHT", on_press = self.mouse_click) )
		middle_buttons_layout.add_widget( Button(text = ">", on_press = self.mouse_move, on_release = self.mouse_release) )
		bottom_button_layout.add_widget( Button(text = "\\/",
			size_hint = (.7, .3),
			halign = "center",
			valign = "bottom",
			on_press = self.mouse_move,
			on_release = self.mouse_release) )


		self.box_layout.add_widget( self.image_layout )
		self.box_layout.add_widget( top_button_layout )
		self.box_layout.add_widget( middle_buttons_layout )
		self.box_layout.add_widget( bottom_button_layout )
		return self.box_layout

	def mouse_move(self, instance):
		self.server.command = "move "
		self.server.button_pressed = True
		text = instance.text
		
		if text == "/\\":
			self.server.command += f"0 {-self.server.cursor_speed}"
		elif text == "<":
			self.server.command += f"{-self.server.cursor_speed} 0"
		elif text == ">":
			self.server.command += f"{self.server.cursor_speed} 0"
		elif text == "\\/":
			self.server.command += f"0 {self.server.cursor_speed}"

		self.server.command = self.server.command.split()

	def mouse_release(self, instance):
		self.server.button_pressed = False

	def mouse_click(self, instance):
		command = "mouse_click "
		text = instance.text

		if text == "LEFT":
			command += "1"
		elif text == "RIGHT":
			command += "2"

		self.server.command = command.split()

	def __exit__(self):
		self.server.stop_flag = True
		self.server.active.close()


if __name__ == "__main__":
	app = ServerApp()
	app.run()