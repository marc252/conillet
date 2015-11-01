#!/usr/bin/env python
from gi.repository import Gtk
import math
import logging
from datetime import datetime
from preferences import Preferences
from rabbitconnection import RabbitConnection
from rabbitparams import RabbitParams
from threading import Thread

class MyHandler(logging.Handler):
    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.widget = widget

    def handle(self, rec):
        #original = self.label.get_text()
        buffer=self.widget.get_buffer()
        end_text = buffer.get_end_iter()
        data = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        buffer.insert(end_text,"\n"+data+"=>"+rec.msg)

class MyLogger():
    def __init__(self, widget):
        self.logger = logging.getLogger("Conillet")
        self.handler = MyHandler(widget)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.addHandler(self.handler)
        self.logger.addHandler(ch)

    def warning(self, msg):
        self.logger.warning(msg)


class Buglump:
    def __init__(self):
        self.amqp_thread = None
        self.gladefile = "conillet.glade" # store the file name
        self.builder = Gtk.Builder() # create an instance of the gtk.Builder
        #self.builder.add_from_file(self.gladefile) # add the xml file to the Builder
        self.builder.add_objects_from_file(self.gladefile,
                ["window1","aboutdialog1","statusbar1","status",
                "log_result","entry1","entry2","result1","logwindow",
                "image1","image2","image3","image4",
                "connection_toggle_button","connection_status_image",
                "message_view"])
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("window1") # This gets the 'window1' object
        self.aboutdialog = self.builder.get_object("aboutdialog1")
        self.log_window = self.builder.get_object("logwindow")
        self.statusbar = self.builder.get_object("statusbar1")
        self.context_id = self.statusbar.get_context_id("status")
        self.connection_toggle_button = self.builder.get_object("connection_toggle_button")
        self.connection_status_image = self.builder.get_object("connection_status_image")
        self.logger_label = self.builder.get_object("log_result")
        self.message_view = self.builder.get_object("message_view")
        self.logger = MyLogger(self.logger_label)
        self.preferences = Preferences(self.builder,self.logger)
        self.rabbit_params = RabbitParams(self.preferences.get_values())
        self.rabbit_connection = RabbitConnection(self.rabbit_params,
                                self.logger, self.connection_toggle_button,
                                self.message_view)
        self.logger.warning("Inici aplicacio")
        self.window.show() # this shows the 'window1' object
        self.status_count=0

    def on_receive_messages_button_toggled(self,button):
        if self.rabbit_connection.isConsuming():
            self.logger.warning("Already consuming messages, stop")
            self.rabbit_connection.stop_consuming()
        else:
            self.logger.warning("Start consuming")
            self.rabbit_connection.start_consuming()

    def on_connection_toggle_button_toggled(self,button):
        if self.rabbit_connection.isConnected():
            self.rabbit_connection.close_connection()
            self.amqp_thread._Thread__stop()
            self.amqp_thread.join()
            #self.connection_status_image.clear()
            self.connection_status_image.set_from_stock("gtk-disconnect",Gtk.IconSize.SMALL_TOOLBAR)
        else:
            self.amqp_thread=Thread(target=self.rabbit_connection.run)
            self.amqp_thread.start()
            self.connection_status_image.set_from_stock("gtk-connect",Gtk.IconSize.SMALL_TOOLBAR)

    def on_logwindow_close_button_clicked(self,button,data=None):
        self.log_window.hide()

    def on_logwindow_delete_event(self,object,event):
        self.log_window.hide()
        return True

    def on_view_log_activate(self,menuitem,data=None):
        self.response = self.log_window.show()

    def on_preferences_activate(self, menuitem,data=None):
        self.response = self.preferences.preferences_window.show()

    def on_gtk_about_activate(self, menuitem, data=None):
        self.logger.warning("help about selected")
        self.response = self.aboutdialog.run()
        self.aboutdialog.hide()

    def on_window1_destroy(self, object, data=None):
        self.logger.warning( "quit with cancel")
        Gtk.main_quit()

    def on_gtk_quit_activate(self, menuitem, data=None):
        print "quit from menu"
        Gtk.main_quit()
        sys.exit()

    def on_push_status_activate(self, menuitem, data=None):
        self.status_count += 1
        self.logger.warning("Ara status count val: %s" % self.status_count)
        self.statusbar.push(self.context_id, "Message number %s" % str(self.status_count))

    def on_pop_status_activate(self, menuitem, data=None):
        self.status_count -= 1
        self.statusbar.pop(self.context_id)

    def on_clear_status_activate(self, menuitem, data=None):
        while (self.status_count > 0):
            self.statusbar.pop(self.context_id)
            self.status_count -= 1


if __name__ == "__main__":
  main = Buglump() # create an instance of our class
  Gtk.main() # run the darn thing
