"""
Monitor do Apple Music para Windows via iTunes COM API
"""
import logging
import time
from typing import Optional, Dict
from dataclasses import dataclass

try:
    import win32com.client
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False
    logging.warning("pywin32 não disponível. Apple Music monitor não funcionará no Windows.")


@dataclass
class TrackInfo:
    """Informações da música atual"""
    title: str
    artist: str
    album: str
    artwork_url: Optional[str] = None
    duration: int = 0
    position: int = 0

    def __eq__(self, other):
        if not isinstance(other, TrackInfo):
            return False
        return (self.title == other.title and
                self.artist == other.artist and
                self.album == other.album)

    def __hash__(self):
        return hash((self.title, self.artist, self.album))


class AppleMusicMonitor:
    """
    Monitora o Apple Music/iTunes no Windows usando COM API
    """

    def __init__(self):
        self.itunes = None
        self.current_track: Optional[TrackInfo] = None
        self.logger = logging.getLogger(__name__)

        if not COM_AVAILABLE:
            raise RuntimeError("pywin32 não está instalado. Instale com: pip install pywin32")

        self._connect()

    def _connect(self):
        """Conecta ao iTunes/Apple Music via COM"""
        try:
            self.itunes = win32com.client.Dispatch("iTunes.Application")
            self.logger.info("Conectado ao iTunes/Apple Music")
        except Exception as e:
            self.logger.error(f"Erro ao conectar ao iTunes/Apple Music: {e}")
            raise

    def get_current_track(self) -> Optional[TrackInfo]:
        """
        Obtém informações da música atual

        Returns:
            TrackInfo ou None se nenhuma música estiver tocando
        """
        try:
            if not self.itunes:
                self._connect()

            current_track = self.itunes.CurrentTrack

            if not current_track:
                return None

            # Tenta obter a URL da artwork
            artwork_url = None
            try:
                artworks = current_track.Artwork
                if artworks and artworks.Count > 0:
                    # A artwork precisa ser salva para ser acessada
                    artwork = artworks.Item(1)
                    # Vamos salvar temporariamente e ler depois
                    artwork_url = "embedded"  # Marcador para processar depois
            except Exception as e:
                self.logger.debug(f"Não foi possível obter artwork: {e}")

            track_info = TrackInfo(
                title=current_track.Name or "Unknown",
                artist=current_track.Artist or "Unknown Artist",
                album=current_track.Album or "Unknown Album",
                artwork_url=artwork_url,
                duration=current_track.Duration,
                position=self.itunes.PlayerPosition
            )

            return track_info

        except Exception as e:
            self.logger.error(f"Erro ao obter música atual: {e}")
            return None

    def save_current_artwork(self, output_path: str) -> bool:
        """
        Salva a capa da música atual em um arquivo

        Args:
            output_path: Caminho para salvar a imagem

        Returns:
            True se salvou com sucesso, False caso contrário
        """
        try:
            if not self.itunes:
                self._connect()

            current_track = self.itunes.CurrentTrack

            if not current_track:
                return False

            artworks = current_track.Artwork
            if artworks and artworks.Count > 0:
                artwork = artworks.Item(1)
                artwork.SaveArtworkToFile(output_path)
                return True

            return False

        except Exception as e:
            self.logger.error(f"Erro ao salvar artwork: {e}")
            return False

    def is_playing(self) -> bool:
        """Verifica se está tocando música"""
        try:
            if not self.itunes:
                self._connect()

            # PlayerState: 0 = Stopped, 1 = Playing
            return self.itunes.PlayerState == 1
        except Exception as e:
            self.logger.error(f"Erro ao verificar estado: {e}")
            return False

    def get_player_info(self) -> Dict:
        """Retorna informações gerais do player"""
        try:
            track = self.get_current_track()

            return {
                "is_playing": self.is_playing(),
                "current_track": track.__dict__ if track else None,
                "volume": self.itunes.SoundVolume if self.itunes else 0
            }
        except Exception as e:
            self.logger.error(f"Erro ao obter informações do player: {e}")
            return {
                "is_playing": False,
                "current_track": None,
                "volume": 0
            }


if __name__ == "__main__":
    # Teste do monitor
    logging.basicConfig(level=logging.DEBUG)

    try:
        monitor = AppleMusicMonitor()

        print("Monitorando Apple Music... (Ctrl+C para sair)")

        while True:
            track = monitor.get_current_track()

            if track:
                print(f"\n🎵 Tocando agora:")
                print(f"   Título: {track.title}")
                print(f"   Artista: {track.artist}")
                print(f"   Álbum: {track.album}")
                print(f"   Duração: {track.duration}s")
                print(f"   Posição: {track.position}s")
            else:
                print("\n⏸️  Nenhuma música tocando")

            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\nEncerrando...")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
