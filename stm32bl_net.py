from socket import socket, AF_INET, SOCK_STREAM

from stm32bl import stm32bls


class stm32bl_net(stm32bls.Stm32bl):
    def __init__(self, url, port=23, verbosity=1):
        self.host = url
        self.port = port
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.sock.settimeout(0.1)
        self._verbosity = verbosity
        self._connect(100)
        self._read(10, 1)

        self._allowed_commands = [self.CMD_GET, ]
        self._boot_version = self._cmd_get()
        self._option_bytes = self._cmd_get_version()
        self._dev_id = self._cmd_get_id()
        self._sn = self._cmd_get_sn()
        self.connected = True

    def info(self):
        return dict(cpuId=self._sn, bootversion=self._boot_version, dev_id=self._dev_id, connected=self.connected)

    def _connect(self, repeat=1):
        """connect to boot-loader"""
        self.log("Connecting to boot-loader", level=1)
        self._reset_mcu()
        while repeat:
            self._write([self.CMD_INIT])
            ret = self._read()
            if ret and ret[0] in (self.CMD_ACK, self.CMD_NOACK):
                return
            repeat -= 1
        raise stm32bls.ConnectingException("Can't connect to MCU boot-loader.")

    def _write(self, data):
        """Write data to serial port"""
        self.log(":".join(['%02x' % d for d in data]), 'WR', level=3)
        self.sock.send(bytes(data))

    def _read(self, cnt=1, timeout=1):
        """Read data from serial port"""
        data = []
        self.sock.settimeout(timeout)

        try:
            data = list(self.sock.recv(cnt))
        except:
            pass
        self.log(":".join(['%02x' % d for d in data]), 'RD', level=3)
        return data

    def _reset_mcu(self):
        """Reset MCU"""
        pass


if __name__ == '__main__':
    stm = stm32bl_net('192.168.31.207')
