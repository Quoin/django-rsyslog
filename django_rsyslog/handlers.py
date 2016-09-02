from logging import handlers
import socket


class OctetCountedSysLogHandler(handlers.SysLogHandler):
    def _emit(self, record):
        try:
            msg = self.format(record)  # + '\000'
            """
            We need to convert record level to lowercase, maybe this will
            change in the future.
            """
            prio = '<%d>1 ' % self.encodePriority(self.facility,
                                                  self.mapPriority(record.levelname))
            # Message is a string. Convert to bytes as required by RFC 5424
            if type(msg) is unicode:
                msg = msg.encode('utf-8')
            content = prio + msg
            full_msg = "%d %s" % (len(content), content)
            if self.unixsocket:
                try:
                    self.socket.send(full_msg)
                except socket.error:
                    self.socket.close()  # See issue 17981
                    self._connect_unixsocket(self.address)
                    self.socket.send(full_msg)
            elif self.socktype == socket.SOCK_DGRAM:
                self.socket.sendto(full_msg, self.address)
            else:
                self.socket.settimeout(1)
                self.socket.sendall(full_msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
