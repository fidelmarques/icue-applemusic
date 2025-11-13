"""
Aplicação principal: Exibe capas do Apple Music no Corsair H150i Elite LCD XT
"""
import logging
import os
import sys
import time
import threading
from pathlib import Path
from typing import Optional

from apple_music_monitor import AppleMusicMonitor, TrackInfo
from image_processor import ImageProcessor
from icue_controller import ICueController, MockICueController


class AppleMusicICueSync:
    """
    Sincroniza capas do Apple Music com o LCD do Corsair
    """

    def __init__(
        self,
        update_interval: float = 2.0,
        fade_duration: float = 1.0,
        lcd_size: tuple = (480, 480),
        cache_dir: str = "./cache",
        use_mock_icue: bool = False
    ):
        """
        Args:
            update_interval: Intervalo de verificação em segundos
            fade_duration: Duração da animação fade em segundos
            lcd_size: Tamanho do LCD
            cache_dir: Diretório de cache
            use_mock_icue: Usar mock do iCUE (para testes sem hardware)
        """
        self.update_interval = update_interval
        self.fade_duration = fade_duration
        self.running = False
        self.logger = logging.getLogger(__name__)

        # Inicializa componentes
        try:
            self.music_monitor = AppleMusicMonitor()
            self.logger.info("✅ Monitor do Apple Music inicializado")
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar monitor do Apple Music: {e}")
            raise

        self.image_processor = ImageProcessor(target_size=lcd_size, cache_dir=cache_dir)
        self.logger.info("✅ Processador de imagens inicializado")

        if use_mock_icue:
            self.icue_controller = MockICueController(lcd_size=lcd_size)
            self.logger.info("✅ Mock iCUE Controller inicializado")
        else:
            self.icue_controller = ICueController(lcd_size=lcd_size)
            self.logger.info("✅ iCUE Controller inicializado")

        self.current_track: Optional[TrackInfo] = None
        self.artwork_cache_path = os.path.join(cache_dir, "temp_artwork.jpg")

    def update_display(self):
        """Atualiza o display com a música atual"""
        try:
            # Obtém a música atual
            track = self.music_monitor.get_current_track()

            # Se não há música ou é a mesma, não faz nada
            if track is None:
                if self.current_track is not None:
                    self.logger.info("⏸️  Música parou, limpando display")
                    self.icue_controller.clear()
                    self.current_track = None
                return

            # Verifica se mudou a música
            if track == self.current_track:
                return

            self.logger.info(f"🎵 Nova música detectada: {track.artist} - {track.title}")

            # Salva a artwork da música atual
            artwork_saved = self.music_monitor.save_current_artwork(self.artwork_cache_path)

            if artwork_saved:
                # Processa a imagem
                image = self.image_processor.process_artwork(
                    self.artwork_cache_path,
                    track_info=track
                )
            else:
                # Usa placeholder se não conseguiu obter a artwork
                self.logger.warning("Não foi possível obter artwork, usando placeholder")
                image = self.image_processor.create_placeholder()

            if image:
                # Atualiza o display com fade
                self.logger.info("🖼️  Atualizando display com fade...")
                self.icue_controller.fade_transition(
                    image,
                    duration=self.fade_duration,
                    fps=30
                )

                # Salva no cache para referência futura
                cache_key = f"{track.artist}_{track.album}".replace("/", "_")
                self.image_processor.save_to_cache(image, cache_key)

            # Atualiza a música atual
            self.current_track = track

        except Exception as e:
            self.logger.error(f"❌ Erro ao atualizar display: {e}", exc_info=True)

    def run(self):
        """Loop principal da aplicação"""
        self.running = True
        self.logger.info("🚀 Aplicação iniciada!")
        self.logger.info(f"   Intervalo de atualização: {self.update_interval}s")
        self.logger.info(f"   Duração do fade: {self.fade_duration}s")

        try:
            while self.running:
                self.update_display()
                time.sleep(self.update_interval)

        except KeyboardInterrupt:
            self.logger.info("\n🛑 Interrompido pelo usuário")
        except Exception as e:
            self.logger.error(f"❌ Erro crítico: {e}", exc_info=True)
        finally:
            self.stop()

    def stop(self):
        """Para a aplicação"""
        self.running = False
        self.logger.info("🔌 Desconectando...")

        try:
            self.icue_controller.disconnect()
        except Exception as e:
            self.logger.error(f"Erro ao desconectar: {e}")

        self.logger.info("✅ Aplicação encerrada")

    def get_status(self) -> dict:
        """Retorna o status atual da aplicação"""
        player_info = self.music_monitor.get_player_info()

        return {
            "running": self.running,
            "current_track": self.current_track.__dict__ if self.current_track else None,
            "player_info": player_info,
            "icue_connected": self.icue_controller.connected,
            "update_interval": self.update_interval,
            "fade_duration": self.fade_duration
        }


def setup_logging(level=logging.INFO):
    """Configura o sistema de logging"""
    # Cria diretório de logs se não existir
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Formato dos logs
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configura logging para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))

    # Configura logging para arquivo
    file_handler = logging.FileHandler(log_dir / "icue_applemusic.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))

    # Configura o logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def main():
    """Função principal"""
    # Configura logging
    setup_logging(level=logging.INFO)

    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Apple Music to iCUE LCD - Iniciando...")
    logger.info("=" * 60)

    # Carrega configurações do ambiente
    from dotenv import load_dotenv
    load_dotenv()

    update_interval = float(os.getenv("UPDATE_INTERVAL", "2.0"))
    fade_duration = float(os.getenv("FADE_DURATION", "1.0"))
    cache_dir = os.getenv("CACHE_DIR", "./cache")

    # Verifica se deve usar mock (útil para desenvolvimento)
    use_mock = os.getenv("USE_MOCK_ICUE", "false").lower() == "true"

    # Cria e executa a aplicação
    try:
        app = AppleMusicICueSync(
            update_interval=update_interval,
            fade_duration=fade_duration,
            cache_dir=cache_dir,
            use_mock_icue=use_mock
        )

        app.run()

    except Exception as e:
        logger.error(f"❌ Falha ao iniciar aplicação: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
