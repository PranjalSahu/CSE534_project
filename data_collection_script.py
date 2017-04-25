# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 00:23:42 2017

@author: Sushant
"""
import time
from random import randint
from subprocess import call
# simulation of a tap on coordinates (x, y) on screen
def adb_touch_tap (x, y):
    cmd =" adb shell input touchscreen tap %s %s" % (x, y)
    call ( cmd . split ())
    return
# simulation of a swipe from coordinates (x1 , y1 ) to (x2 , y2) on screen
def adb_touch_swipe (x1 , y1 , x2 , y2 , speed ):
    param =(x1 , y1 , x2 , y2 , speed )
    cmd =" adb shell input touchscreen swipe %s %s %s %s %s" % ( param )
    call ( cmd . split ())
    return
# simulation of keyboard button press identified by " code "
def adb_keycode ( code ):
    cmd =" adb shell input keyevent KEYCODE_ %s" % ( code )
    call ( cmd . split ())
    return
# sending a signal to kill a process
def kill ( process ):
    cmd =" adb shell am force - stop %s" % ( process )
    call ( cmd . split ())
    return



def open_facebook(f):
    #go to home
    adb_touch_tap(370, 1240)
    time.sleep(5)
    
    cmd =" adb shell am force-stop com.facebook.katana"
    call ( cmd . split ())
    
    f.write(str(time.time()) + " : open_facebook starts\n")
    #launch fb app
    adb_touch_tap(440, 670)

def facebook_post(i):
    
    #tap on whats on your mind:           
    adb_touch_tap(353, 507)
    time.sleep(5)

    #focus
    adb_touch_tap(120, 360)
    time.sleep(5)

    #type some crap
    getStatus(i)
    
    time.sleep(2)

    #post
    adb_touch_tap(650, 100)
    
def open_user_profile():
    #tap on search 
    adb_touch_tap(247, 95)
    time.sleep(5)
    
    letter = randint(29,49)
    adb_keycode(letter)  
    time.sleep(5)
    
    adb_touch_tap(229,203)
    time.sleep(5)
    
    adb_touch_tap(118, 441)
    
def send_message():
    adb_touch_tap(670, 114)
    time.sleep(5)
    
    adb_touch_tap(255, 111)
    adb_keycode(44)
    adb_keycode(46) 
    adb_keycode(29) 
    time.sleep(5)
    adb_touch_tap(305, 223)
    adb_touch_tap(229, 1166)
    time.sleep(5)
    
    write_message()

def write_message():
    message_length = randint(5,30)
    for i in range(1,message_length):
        letter = randint(29,54)
        adb_keycode(letter)
    adb_touch_tap(683,636)
    
def getStatus(i):
    f2= open('sentences.txt', 'r')
    lines = f2.readlines()
    lines = [x.strip() for x in lines]
    
    status_num = len(lines)
    statusn = randint(0, status_num-1)
    
    status = lines[i]
    firstpart, secondpart = status[:len(status)/2], status[len(status)/2:]
    status = firstpart
    status = status.replace(' ', '%s')
    
    cmd ="adb shell input text %s" % ( status )
    print cmd
    call ( cmd.split() )
    print status
    
#def post_on_other_wall():
#    open_facebook()
#    #tap on search 
#    adb_touch_tap(247, 95)
#    time.sleep(5)
#    
#    adb_keycode(44)
#    adb_keycode(46) 
#    adb_keycode(29) 
#    time.sleep(5)
#    
#    adb_touch_tap(229,203)
#    time.sleep(5)
#    
#    adb_touch_tap(118, 441)
#



for i in range(9,30):
    f = open('traffic.txt', 'a')
    f.write(str(time.time()) + " : emulator starts for iteration " + str(i) + "\n")
    

    open_facebook(f)
    f.write(str(time.time()) + " : open_facebook ends\n")
    time.sleep(10)
    
    f.write(str(time.time()) + " : post_on_wall starts\n")
    facebook_post(i)
    f.write(str(time.time()) + " : post_on_wall ends\n")
    time.sleep(10)
    
    open_facebook(f)
    f.write(str(time.time()) + " : open_facebook ends\n")
    time.sleep(10)
    
    f.write(str(time.time()) + " : open_user_profile starts\n")
    open_user_profile()
    f.write(str(time.time()) + " : open_user_profile ends\n")
    time.sleep(10)
    
    
    open_facebook(f)
    f.write(str(time.time()) + " : open_facebook ends\n")
    time.sleep(10)
    
    f.write(str(time.time()) + " : send_message starts\n")
    send_message()
    f.write(str(time.time()) + " : send_message ends\n")
    time.sleep(10)
    
    f.write(str(time.time()) + " :emulator close for iteration " + str(i) + "\n")

    print i
    
    f.close()

#getStatus()
#

    