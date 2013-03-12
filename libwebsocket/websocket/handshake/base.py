
class Base(object):

    @property:
    def host(self):
        return self._host
    @property
    def port(self):
        return self._port
    @property
    def path(self):
        return self._path
    @property
    def error(self):
        return self._error
    @property
    def state(self):
        return self._state
    @property
    def version(self):
        return self._version
    @property
    def secure(self):
        return self._secure


    def __init__ (self, *args, **kwargs):
        super(Base, self).__init__(*args, **kwargs)
        self._state = intern("new")
        self._data = ""
        self._headers = {}
    
    def append(self, data):
        self._data.append(data)

    # Is parsing of data finished?
    # @return [Boolena] True if request was completely parsed or error occured. False otherwise
    def finished(self):
        if self.state == intern("finished") or self.state == intern("error"):
            return True
        return False

    # Is parsed data valid?
    # @return [Boolean] False if some errors occured. Reason for error could be found in error method
    def valid(self):
        if self.finished() == True or self.error is not None:
            return True
        return False

    # @abstract Should send data after parsing is finished?
    def should_respond(self):
        raise NotImplementedError

    # Data left from parsing. Sometimes data that doesn't belong to handshake are added - use this method to retrieve them.
    # @return [String] String if some data are available. Nil otherwise
    def leftovers(self):
        self._leftovers.split("\n", self.reserved_leftover_lines + 1)[self.reserved_leftover_lines]

    # Number of lines after header that should be handled as belonging to handshake. Any data after those lines will be handled as leftovers.
    # @return [Integer] Number of lines
    @property
    def reserved_leftover_lines
        return 0
