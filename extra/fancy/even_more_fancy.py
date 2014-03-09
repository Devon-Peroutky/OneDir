__author__ = 'Justin Jansen'
__status__ = 'Prototype'
__date__ = '03/08/14'

import os
import gtk
import appindicator as appi
import subprocess


def main():
    ind = appi.Indicator("OneDIR", "Notify message", appi.CATEGORY_APPLICATION_STATUS)
    ind.set_status(appi.STATUS_ACTIVE)
    d = os.getcwd() + "/tiny_strip.png"
    ind.set_icon(str(d))
    ind.set_attention_icon("indicator-messages-new")
    menu = gtk.Menu()
    item = gtk.MenuItem("OneDir Notification such as SYNC'ing")
    menu.append(item)
    item.show()
    ind.set_menu(menu)
    gtk.main()


if __name__ == '__main__':
    command = 'notify-send "This is not what I wanted you to notice" ' \
              '"Look up and slightly to the left, for the new icon." -t 5000'
    subprocess.Popen(command, shell=True)
    main()
