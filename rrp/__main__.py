from click import group, option
from flask import Flask, Response, stream_with_context
from yaml import safe_load
from requests import get


DEFAULT_STATIONS_HOST = 'localhost'
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 8080

STREAMING_CHUNK_SIZE = 2048


class HttpServer:
    def __init__(self, config: dict, name: str = 'Radio Renaissance Proxy', stations_host: str = DEFAULT_STATIONS_HOST, host = DEFAULT_HOST, port = DEFAULT_PORT):
        self.config = config

        self.app = Flask(name)
        self.name = name

        self.stations_host = stations_host
        self.host = host
        self.port = port

    def _make_stream_url(self, station: str):
        config = self.config

        return f'http://{self.stations_host}:{config[station]["stream"]["port"]}/radio.mp3'

    def _handle_stream(self, station: str):
        req = get(self._make_stream_url(station), stream = True)

        return Response(
            stream_with_context(req.iter_content(chunk_size = STREAMING_CHUNK_SIZE))
        )

    def start(self):
        app = self.app

        @app.route('/v1/pranks/stream')
        def pranks_stream():
            return self._handle_stream('pranks')

            # req = get(self._make_stream_url('pranks'), stream = True)

            # return Response(
            #     stream_with_context(req.iter_content(chunk_size = STREAMING_CHUNK_SIZE))
            # )

        @app.route('/v1/anus/stream')
        def anus_stream():
            return self._handle_stream('anus')

            # req = get(self._make_stream_url('anus'), stream = True)

            # return Response(
            #     stream_with_context(req.iter_content(chunk_size = STREAMING_CHUNK_SIZE))
            # )

        @app.route('/v1/314/stream')
        def _314_stream():
            return self._handle_stream(314)

        @app.route('/v1/2ch/stream')
        def _2ch_stream():
            return self._handle_stream('2ch')

        @app.route('/v1/baneks/stream')
        def baneks_stream():
            return self._handle_stream('baneks')

        @app.route('/v1/books/stream')
        def books_stream():
            return self._handle_stream('books')

        app.run(host = self.host, port = self.port)


@group()
def main():
    pass


@main.command()
@option('--stations-host', '-s', type = str, default = 'localhost')
@option('--stations-config-path', '-c', type = str, default = 'assets/stations.yml')
@option('--port', '-p', type = int, default = 8080)
def start(stations_host: str, stations_config_path: str, port: int):
    with open(stations_config_path, 'r', encoding = 'utf-8') as file:
        config = safe_load(file)

    print(config)

    HttpServer(config, stations_host = stations_host, port = port).start()


if __name__ == '__main__':
    main()
