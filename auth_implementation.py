import Murmur

class AuthenticatorAttacher(Murmur.MetaCallback):
    def __init__(self, app, print_debug):
        self.app = app
        self.print_debug = print_debug
        super().__init__()

    def started(server):
        self.app.attachAuthenticator(server)

    def stopped(server):
        servers_on = self.app.meta.getBootedServers()
        if len(servers_on) == 0:
            self.print_debug("No servers on. Shutting down.")
            self.app.communicator().shutdown()

class StadiumAuthenticator(Murmur.ServerAuthenticator):
    def __init__(self, app, server, print_debug):
        self.app = app
        self.print_debug = print_debug
        self.server = server
        super().__init__()

    def authenticate(self, name, pw, certs, certhash, certstrong, newname = None, groups = None):
        try:
            if name == "SuperUser":
                return(-2, None, None)

            record = self.app.db_abs.get_user_by_password(pw)

            if record == None:
                self.print_debug("Authentication failed with password ", pw)
                return(-1, None, None)

            mumble_name = record[1]
            _id = record[0]

            # Don't check if the user is already connected. Mumble will deal with that.

            # already_connected = False
            #
            # try:
            #     user_state = self.server.getState(_id)
            # except:
            #     already_connected = True
            #
            # if already_connected: return (-1, None, None)

            self.print_debug("Authentication succeeded, user's mumble name is ", record[1])
            return (_id, mumble_name, None)
        except:
            return(-1, None, None)

    def nameToId(self, name, current = None):
        # fallthrough
        return -2

    def idToName(self, id):
        # fallthrough
        return ""

    def getInfo(self, id, current = None):
        # fallthrough
        return (False, None)
