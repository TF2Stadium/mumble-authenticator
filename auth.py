import sys, traceback, Ice
import Murmur
import configparser
import time
import os
from auth_implementation import *
from db import *
from threading import Timer

CHECK_CONNECTION_INTERVAL = 5.0
RECONNECT_INTERVAL = 5.0
DEBUG_FLAG = False
def print_debug(*text):
    if DEBUG_FLAG: print(*text)

class StadiumAuthenticatorApp(Ice.Application):
    def __init__(self, config, db_abs):
        self.config = config
        self.db_abs = db_abs
        self.shutDownByForce = False
        super().__init__()

    def run(self, args):
        if not self.initialize():
                return 1

        self.connectionChecker = Timer(CHECK_CONNECTION_INTERVAL, self.checkConnection)
        self.connectionChecker.start()

        self.communicator().waitForShutdown()
        if self.interrupted():
            self.connectionChecker.cancel()

        if self.shutDownByForce:
            raise RuntimeError("Couldn't get a response from server")

        return 0

    # self.meta: holds the meta object pointer

    def attachAuthenticator(self, server):
        print("Attaching the authenticator to a server")
        authcbprx = self.adapter.addWithUUID(StadiumAuthenticator(self, server, print_debug))
        self.authcb = Murmur.ServerAuthenticatorPrx.uncheckedCast(authcbprx)
        server.setAuthenticator(self.authcb)

    def checkConnection(self):
        try:
            # print_debug("Checking for up")
            self.meta.getUptime()
            self.connectionChecker = Timer(CHECK_CONNECTION_INTERVAL, self.checkConnection)
            self.connectionChecker.start()
        except:
            print("Couldn't get a response from the server. Terminating.")
            self.communicator().shutdown()
            self.shutDownByForce = True

    def initialize(self):
        ic = self.communicator()

        if 'mumble' not in self.config or 'secret' not in self.config['mumble']:
            raise RuntimeError("Read and write secrets must be entered")

        ic.getImplicitContext().put("secret", self.config['mumble']['secret'])

        proxy = ic.stringToProxy("Meta:tcp -h {} -p {}".format(self.config['mumble']['host'], self.config['mumble']['port']))

        self.meta = Murmur.MetaPrx.checkedCast(proxy)
        if self.meta == None:
            raise RuntimeError("Invalid proxy")

        self.adapter = ic.createObjectAdapterWithEndpoints("AuthAdapter", "tcp -h {}".format(self.config['mumble']['host']))
        self.adapter.activate()

        metacbprx = self.adapter.addWithUUID(AuthenticatorAttacher(self, print_debug))
        self.metacb = Murmur.MetaCallbackPrx.uncheckedCast(metacbprx)
        self.meta.addCallback(self.metacb)

        for server in self.meta.getBootedServers():
            self.attachAuthenticator(server)

        return True

if __name__ == "__main__":
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')

        DEBUG_FLAG = (config['general']['debug'] == 'true')
        CHECK_CONNECTION_INTERVAL = float(config['general']['check_connection_interval'])
        RECONNECT_INTERVAL = float(config['general']['reconnect_interval'])

        db_abs = DbWrapper(config['database']['db_string'], config['database']['table'])

        app = StadiumAuthenticatorApp(config, db_abs)

        state = app.main(sys.argv + ['--Ice.Default.EncodingVersion=1.0', '--Ice.ImplicitContext=Shared'])
        if state != 0:
            raise RuntimeError("Ice app exited with non-zero return value")
    except:
        traceback.print_exc()
        print_debug("Authentication handler disconnected. Trying to reconnect in {} seconds...".format(RECONNECT_INTERVAL))
        time.sleep(RECONNECT_INTERVAL)

        # restart the script (try to reconnect)
        os.execv(sys.executable, [sys.executable] + sys.argv)
