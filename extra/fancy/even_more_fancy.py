import gobject
import gtk
import appindicator as appi
import subprocess
import webbrowser
import sys
import os

def wp_launcher(widget):
    cwd = os.getcwd()
    url = 'file://' + cwd + '/index.html'
    webbrowser.open_new(url)

def quit(widget):
    sys.exit(0)

def main():
    ind = appi.Indicator("OneDIR", "Notify message", appi.CATEGORY_APPLICATION_STATUS)
    ind.set_status(appi.STATUS_ACTIVE)
    ind.set_icon("/home/justin/tiny_strip.png")
    ind.set_attention_icon("indicator-messages-new")
    menu = gtk.Menu()
    title = gtk.MenuItem("OneDir Notification: (click below)")
    notif = gtk.MenuItem("A friend invited you to share a folder")
    q = gtk.MenuItem("quit")
    notif.connect("activate", wp_launcher)
    q.connect("activate", quit)
    menu.append(title)
    menu.append(notif)
    menu.append(q)
    title.show()
    notif.show()
    q.show()
    ind.set_menu(menu)
    gtk.main()

if __name__ == '__main__':
    command = 'notify-send "This is not what I wanted you to notice" "Look up and slightly to the left for the Thunderbird icon. \n I am using that icon as a placeholder for now" -t 5000'
    subprocess.Popen(command, shell=True)
    main()