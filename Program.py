import sys
import telnetlib
import psutil
import signal
import binascii
import regex as re
import OogaAPI as oob
from termcolor import colored
from time import sleep
from os import path

# Config
tn_host = "127.0.0.1" # CSGO telnet stuffs
tn_port = "2121"
cfg_path = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Counter-Strike Global Offensive\\csgo\\cfg\\" # Path to CSGO config goes here
user = "Example" # Your CSGO Username to avoid infinite looping (just the base name, no clan or anything else)


def signal_handler(signal, frame):
	print("\nquitting...")
	sys.exit(0)

# List PIDs of processes matching processName
def processExists(processName):
	procList = []
	for proc in psutil.process_iter(['name']):
		if proc.info['name'].lower() == processName.lower():
			return True
	return False

# Runs commands on the CS:GO console
def run(txn, command):
	cmd_s = command + "\n"
	txn.write(cmd_s.encode('utf-8'))
	sleep(0.005)

signal.signal(signal.SIGINT, signal_handler)

def main():
	awaiting_user_message = False
	reply_status = True #If bot replies to enemy and teammate messages (true = it does)
	infinite_chat_mode = False #If bot replies to itself (true = it replies)

	if (len(sys.argv) > 1):
		if (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
			print(colored("Run with no arguments to initiate and connect to csgo", attrs=['bold']))
			print(colored("Make sure you set up csgo to receive connections with this launch option: -netconport "+str(tn_port), attrs=['bold']))
	
	# Make sure CS:GO is running before trying to connect
	if not processExists("csgo.exe"):
		print("Waiting for csgo to start... ")
		while not processExists("csgo.exe"):
			sleep(0.25)
		sleep(10)

	# Initialises CS:GO telnet connection
	print("Trying to connect to " + tn_host + ":" + tn_port)
	try:
		tn = telnetlib.Telnet(tn_host, tn_port)
	except ConnectionRefusedError:
		sleep(30)
		pass
	try:
		tn = telnetlib.Telnet(tn_host, tn_port)
	except ConnectionRefusedError:
		print("Connection refused. Don't forget to add -netconport " + str(tn_port) + " to launch options.")
		sys.exit(1)
	print("Successfully Connected")

	print("Listening for messages...")
	while True:
		try:
			result = tn.expect([b"\r\n"])
			last_line = result[2].decode("utf-8").splitlines()
			last_line = last_line[len(last_line) - 1]
			# Special characters used to determine what and where chat messages start and end.
			if "‎" in last_line and "​" not in last_line:
				whole_line = last_line
				last_line = last_line.split("‎")

				# Parses the name
				sender = str(last_line[0])
				sender = sender.replace("(Counter-Terrorist) ", "")
				sender = sender.replace("(Terrorist) ", "")
				sender = sender.replace("*DEAD* ", "")
				sender = sender.replace("*DEAD*", "")
				sender = sender.replace("*SPEC* ", "")
				sender = sender.replace("(Spectator) ", "")

				message = str(last_line[1])
				message = re.sub(r'^.*? : ', '', message)
				message = re.sub(r"^\s+", "", message)
				
				if message == 'OogaMenu' and sender == user:
					awaiting_user_message = True
					sleep(1)
					run(tn, "say 0 - Toggle ooga replies (currently set to " + str(reply_status) + ")")
					sleep(1)
					run(tn, "say 1 - Toggle infinite chat mode (currently set to " + str(infinite_chat_mode) + ")")
					sleep(1)
					run(tn, "say 2 - Close menu")

				if awaiting_user_message == True and sender == user:
					if message == '0':
						reply_status = not reply_status
						awaiting_user_message = False
						sleep(1)
						run(tn, "say Ooga reply status set to " + str(reply_status))
					if message == '1':
						infinite_chat_mode = not infinite_chat_mode
						awaiting_user_message = False
						sleep(1)
						run(tn, "say Infinite chat mode set to " + str(infinite_chat_mode))
					if message == '2':
						awaiting_user_message = False
						sleep(1)
						run(tn, "say Menu Closed")
				
				if awaiting_user_message == False and reply_status == True:
					if sender == user and infinite_chat_mode == False:
						if message[:7] == 'prompt:':
							print(sender + " : " + message)
							message = message[7:]
							response = oob.getResponse(message)
							run(tn, "say " + response)
							print("AI : " + response)
						else:
							print(sender + " : " + message)
							pass
					else:
						print(sender + " : " + message)
						response = oob.getResponse(message)
						run(tn, "say " + response)
						print("AI : " + response)
		except Exception as e:
			print("Something went wrong. Make sure -netconport " + str(tn_port) + " is added to launch options.")
			print(e)
			sys.exit(1)


if __name__== "__main__":
  main()
