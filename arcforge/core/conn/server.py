import threading
import socket
import logging
import time
from http.server import HTTPServer, ThreadingHTTPServer
from arcforge.core.conn.handler import RouteHandler

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Singleton(type):
    _instances = {}
    _lock = threading.Lock()  # Lock para evitar problemas em ambientes multithread

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class WebServer(metaclass=Singleton):
    def __init__(self, host="localhost", port=9090, threaded=True):
        self.host = host
        self.port = port
        self.server_address = (self.host, self.port)
        self._is_running = False

        # Verifica se a porta está em uso antes de iniciar o servidor
        if self.is_port_in_use():
            raise RuntimeError(f"A porta {self.port} já está em uso. Escolha outra porta.")

        # Define o servidor HTTP, podendo ser multithreaded
        ServerClass = ThreadingHTTPServer if threaded else HTTPServer
        self.httpd = ServerClass(self.server_address, RouteHandler)
        self.start()

    def is_port_in_use(self):
        """Verifica se a porta está em uso"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)  # Evita bloqueios
                return s.connect_ex((self.host, self.port)) == 0
        except OSError as e:
            logging.error(f"Erro ao verificar a porta {self.port}: {e}")
            return True  # Assume que a porta está ocupada por segurança

    def start(self):
        """Inicia o servidor se ele não estiver rodando"""
        if self._is_running:
            logging.warning("Servidor já está rodando.")
            return

        try:
            logging.info(f"Servidor rodando em http://{self.host}:{self.port}")
            self._is_running = True
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            logging.error(f"Erro inesperado no servidor: {e}")
            self.stop()

    def stop(self):
        """Para o servidor com segurança"""
        if self._is_running:
            logging.info("Encerrando o servidor...")
            try:
                self.httpd.shutdown()
                self.httpd.server_close()
                self._is_running = False
                logging.info("Servidor encerrado com sucesso.")
            except Exception as e:
                logging.error(f"Erro ao encerrar o servidor: {e}")
        else:
            logging.warning("Servidor não estava rodando.")



# Exemplo de uso
if __name__ == "__main__":
    server = WebServer(port=9090)  # Pode modificar a porta se necessário
    server.start()
