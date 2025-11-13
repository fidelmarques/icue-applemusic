"""
API REST para monitoramento e controle
"""
import logging
import os
import platform
import threading
from flask import Flask, jsonify, request, send_file
from dotenv import load_dotenv

from main import AppleMusicICueSync

# Carrega variáveis de ambiente
load_dotenv()

# Configura Flask
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Logger
logger = logging.getLogger(__name__)

# Instância global da aplicação
sync_app: AppleMusicICueSync = None
sync_thread: threading.Thread = None


def init_sync_app():
    """Inicializa a aplicação de sincronização"""
    global sync_app

    update_interval = float(os.getenv("UPDATE_INTERVAL", "2.0"))
    fade_duration = float(os.getenv("FADE_DURATION", "1.0"))
    cache_dir = os.getenv("CACHE_DIR", "./cache")
    use_mock = os.getenv("USE_MOCK_ICUE", "false").lower() == "true"

    sync_app = AppleMusicICueSync(
        update_interval=update_interval,
        fade_duration=fade_duration,
        cache_dir=cache_dir,
        use_mock_icue=use_mock
    )


def start_sync_thread():
    """Inicia a thread de sincronização"""
    global sync_thread

    if sync_thread and sync_thread.is_alive():
        logger.warning("Thread de sincronização já está rodando")
        return

    sync_thread = threading.Thread(target=sync_app.run, daemon=True)
    sync_thread.start()
    logger.info("Thread de sincronização iniciada")


@app.route("/")
def index():
    """Endpoint raiz"""
    return jsonify({
        "service": "Apple Music to iCUE LCD",
        "version": "1.0.0",
        "endpoints": {
            "/status": "GET - Status atual da aplicação",
            "/current": "GET - Música atual",
            "/start": "POST - Inicia a sincronização",
            "/stop": "POST - Para a sincronização",
            "/config": "GET/POST - Configurações"
        }
    })


@app.route("/status")
def status():
    """Retorna o status da aplicação"""
    if not sync_app:
        return jsonify({
            "error": "Aplicação não inicializada"
        }), 503

    return jsonify(sync_app.get_status())


@app.route("/current")
def current():
    """Retorna informações da música atual"""
    if not sync_app:
        return jsonify({
            "error": "Aplicação não inicializada"
        }), 503

    track = sync_app.current_track

    if not track:
        return jsonify({
            "playing": False,
            "track": None
        })

    return jsonify({
        "playing": True,
        "track": {
            "title": track.title,
            "artist": track.artist,
            "album": track.album,
            "duration": track.duration,
            "position": track.position
        }
    })


@app.route("/start", methods=["POST"])
def start():
    """Inicia a sincronização"""
    if not sync_app:
        init_sync_app()

    if sync_app.running:
        return jsonify({
            "message": "Sincronização já está rodando"
        })

    start_sync_thread()

    return jsonify({
        "message": "Sincronização iniciada"
    })


@app.route("/stop", methods=["POST"])
def stop():
    """Para a sincronização"""
    if not sync_app or not sync_app.running:
        return jsonify({
            "message": "Sincronização não está rodando"
        })

    sync_app.stop()

    return jsonify({
        "message": "Sincronização parada"
    })


@app.route("/config", methods=["GET", "POST"])
def config():
    """Obtém ou atualiza configurações"""
    if request.method == "GET":
        return jsonify({
            "update_interval": sync_app.update_interval if sync_app else 2.0,
            "fade_duration": sync_app.fade_duration if sync_app else 1.0,
            "use_mock_icue": os.getenv("USE_MOCK_ICUE", "false")
        })

    # POST - atualiza configurações
    data = request.json

    if sync_app:
        if "update_interval" in data:
            sync_app.update_interval = float(data["update_interval"])

        if "fade_duration" in data:
            sync_app.fade_duration = float(data["fade_duration"])

    return jsonify({
        "message": "Configurações atualizadas",
        "config": {
            "update_interval": sync_app.update_interval if sync_app else 2.0,
            "fade_duration": sync_app.fade_duration if sync_app else 1.0
        }
    })


@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "sync_running": sync_app.running if sync_app else False
    })


def run_api_server():
    """Executa o servidor API"""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    logger.info(f"🌐 Iniciando servidor API em {host}:{port}")

    # Inicializa a aplicação
    init_sync_app()

    # Inicia a sincronização automaticamente
    start_sync_thread()

    # Executa o servidor
    app.run(host=host, port=port, debug=debug, use_reloader=False)


if __name__ == "__main__":
    from main import setup_logging
    setup_logging(level=logging.INFO)

    run_api_server()
