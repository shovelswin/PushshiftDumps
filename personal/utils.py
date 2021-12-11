import zstandard
import json


def read_obj_zst(file_name):
	with open(file_name, 'rb') as file_handle:
		buffer = ''
		reader = zstandard.ZstdDecompressor(max_window_size=2**31).stream_reader(file_handle)
		while True:
			chunk = reader.read(2**27).decode()
			if not chunk:
				break
			lines = (buffer + chunk).split("\n")

			for line in lines[:-1]:
				yield json.loads(line)

			buffer = lines[-1]
		reader.close()


def read_obj_zst_meta(file_name):
	with open(file_name, 'rb') as file_handle:
		buffer = ''
		reader = zstandard.ZstdDecompressor(max_window_size=2**31).stream_reader(file_handle)
		while True:
			chunk = reader.read(2**27).decode()
			if not chunk:
				break
			lines = (buffer + chunk).split("\n")

			for line in lines[:-1]:
				try:
					json_object = json.loads(line)
				except (KeyError, json.JSONDecodeError) as err:
					continue
				yield json_object, line, file_handle.tell()

			buffer = lines[-1]
		reader.close()


class OutputZst:
	def __init__(self, file_name):
		output_file = open(file_name, 'wb')
		self.writer = zstandard.ZstdCompressor().stream_writer(output_file)

	def write(self, line):
		encoded_line = line.encode('utf-8')
		self.writer.write(encoded_line)

	def close(self):
		self.writer.close()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, exc_traceback):
		self.close()
		return True
