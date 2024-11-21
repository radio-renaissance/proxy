from click import group, option
from flask import Flask, Response, stream_with_context
from yaml import safe_load
from requests import get
from flask_cors import CORS


DEFAULT_STATIONS_HOST = 'localhost'
DEFAULT_STATIONS_PORT = 8080

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 8080

STREAMING_CHUNK_SIZE = 2048


class HttpServer:
    def __init__(
        self, config: dict, name: str = 'Radio Renaissance Proxy',
        stations_host: str = DEFAULT_STATIONS_HOST, stations_port = DEFAULT_STATIONS_PORT,
        host = DEFAULT_HOST, port = DEFAULT_PORT
    ):
        self.config = config

        self.app = app = Flask(name)
        CORS(app)

        self.name = name

        self.stations_host = stations_host
        self.stations_port = stations_port

        self.host = host
        self.port = port

    def _make_stream_url(self, station: str):
        config = self.config

        return f'http://{self.stations_host}:{config[station]["stream"]["port"]}/radio.mp3'

    def _make_meta_url(self, station: str):
        return f'http://{self.stations_host}:{self.stations_port}/api/nowplaying/{station}'

    def _handle_stream(self, station: str):
        req = get(self._make_stream_url(station), stream = True)

        return Response(
            stream_with_context(req.iter_content(chunk_size = STREAMING_CHUNK_SIZE))
        )

    def _handle_meta(self, station: str):
        meta = get(
            self._make_meta_url(station)
        )

        json = meta.json()

        now_playing = json['now_playing']

        return {
            'duration': now_playing['duration'],
            'elapsed': now_playing['elapsed'],
            'remaining': now_playing['remaining'],
            'artist': now_playing['song']['artist'],
            'title': now_playing['song']['title'],
            'id': now_playing['song']['id'],
            'art-id': now_playing['song']['art'].split('/')[-1].split('-')[0]
        }

    def start(self):
        app = self.app

        @app.route('/v1/pranks/stream')
        def pranks_stream():
            return self._handle_stream('pranks')

        @app.route('/v1/pranks/meta')
        def pranks_meta():
            return self._handle_meta('pranks')

        @app.route('/v1/anus/stream')
        def anus_stream():
            return self._handle_stream('anus')

        @app.route('/v1/anus/meta')
        def anus_meta():
            return self._handle_meta('anus')

        @app.route('/v1/314/stream')
        def _314_stream():
            return self._handle_stream(314)

        @app.route('/v1/314/meta')
        def _314_meta():
            return self._handle_meta('station_314')

        @app.route('/v1/2ch/stream')
        def _2ch_stream():
            return self._handle_stream('2ch')

        @app.route('/v1/2ch/meta')
        def _2ch_meta():
            return self._handle_meta('2ch')

        @app.route('/v1/baneks/stream')
        def baneks_stream():
            return self._handle_stream('baneks')

        @app.route('/v1/baneks/meta')
        def baneks_meta():
            return self._handle_meta('baneks')

        @app.route('/v1/books/stream')
        def books_stream():
            return self._handle_stream('books')

        @app.route('/v1/books/meta')
        def books_meta():
            return self._handle_meta('books')

        app.run(host = self.host, port = self.port)


@group()
def main():
    pass


@main.command()
@option('--stations-host', '-s', type = str, default = DEFAULT_STATIONS_HOST)
@option('--stations-port', '-o', type = str, default = DEFAULT_STATIONS_PORT)
@option('--stations-config-path', '-c', type = str, default = 'assets/stations.yml')
@option('--port', '-p', type = int, default = 8080)
def start(stations_host: str, stations_port: int, stations_config_path: str, port: int):
    with open(stations_config_path, 'r', encoding = 'utf-8') as file:
        config = safe_load(file)

    HttpServer(config, stations_host = stations_host, stations_port = stations_port, port = port).start()


if __name__ == '__main__':
    main()
