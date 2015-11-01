#panell de preferencies
import ConfigParser
CFGFILE="prefs.cfg"

class Preferences:
    def __init__(self,builder,logger):
        self.gladefile = "conillet.glade"
        self.config = ConfigParser.ConfigParser()
        self.logger = logger
        self.builder = builder
        self.builder.add_objects_from_file(self.gladefile,
                                ["preferences_window","server_entry",
                                "port_entry","user_entry","pass_entry",
                                "exchange_entry","routing_key_entry",
                                "queue_name_entry","save_response_dialog"])
        self.preferences_window = self.builder.get_object("preferences_window")
        self.save_response_dialog = self.builder.get_object("save_response_dialog")
        self.server_entry = self.builder.get_object("server_entry")
        self.port_entry = self.builder.get_object("port_entry")
        self.user_entry = self.builder.get_object("user_entry")
        self.pass_entry = self.builder.get_object("pass_entry")
        self.exchange_entry = self.builder.get_object("exchange_entry")
        self.routing_key_entry = self.builder.get_object("routing_key_entry")
        self.queue_name_entry = self.builder.get_object("queue_name_entry")
        self.builder.connect_signals(self)
        self.get_config()

    def get_values(self):
        return {"server" : self.server_entry.get_text(),
                "port" : self.port_entry.get_text(),
                "user" : self.user_entry.get_text(),
                "pass" : self.pass_entry.get_text(),
                "exchange" : self.exchange_entry.get_text(),
                "routing_key" : self.routing_key_entry.get_text(),
                "queue_name" : self.queue_name_entry.get_text()
                }
    def get_config(self):
        try:
            self.config.read(CFGFILE)
            self.server_entry.set_text(self.config.get("rabbit","server"))
            self.port_entry.set_text(self.config.get("rabbit","port"))
            self.user_entry.set_text(self.config.get("rabbit","user"))
            self.pass_entry.set_text(self.config.get("rabbit","password"))
            self.exchange_entry.set_text(self.config.get("rabbit","exchange"))
            self.routing_key_entry.set_text(self.config.get("rabbit","routing_key"))
            self.queue_name_entry.set_text(self.config.get("rabbit","queue_name"))
        except SyntaxError as se:
            self.logger.warning("SyntaxError reading config file: %s" % se)
        except AttributeError as ae:
            self.logger.warning("AttributeError reading config file: %s" % ae)
        except ConfigParser.NoOptionError as ce:
            self.logger.warning("NoOptionError reading config file: %s" % ce)
        except Exception as e:
            self.logger.warning("Execpcio llegint config: %s" % e)
            self.logger.warning("No existeix el fitxer de configuracio, el creem")
            self.save_config()

    def save_config(self):
            cfgfile=open(CFGFILE,'w')
            self.config.remove_section("rabbit")
            self.config.add_section("rabbit")
            self.config.set('rabbit','server',str(self.server_entry.get_text()))
            self.config.set('rabbit','port',str(self.port_entry.get_text()))
            self.config.set('rabbit','user',str(self.user_entry.get_text()))
            self.config.set('rabbit','password',str(self.pass_entry.get_text()))
            self.config.set('rabbit','exchange',str(self.exchange_entry.get_text()))
            self.config.set('rabbit','routing_key',str(self.routing_key_entry.get_text()))
            self.config.set('rabbit','queue_name',str(self.queue_name_entry.get_text()))
            self.config.write(cfgfile)
            cfgfile.close()
            self.save_response_dialog.show()

    def on_ok_save_dialog_clicked(self,button,data=None):
        self.save_response_dialog.close()

    def on_save_config_button_clicked(self,button,data=None):
        self.save_config()


    def on_preferences_window_delete_event(self,object,event):
        self.preferences_window.hide()
        return True

    def on_prefs_close_button_clicked(self,button,data=None):
        self.preferences_window.hide()

    def on_test_button_clicked(self,button,data=None):
        print "test clicked"
        self.logger.warning("hem fet un test")
