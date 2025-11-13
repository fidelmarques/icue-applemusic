"""
Monitor do Apple Music para macOS usando AppleScript
"""
import logging
import subprocess
from typing import Optional, Dict
from dataclasses import dataclass


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


class AppleMusicMonitorMacOS:
    """
    Monitora o Apple Music no macOS usando AppleScript
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.current_track: Optional[TrackInfo] = None
        self.logger.info("AppleScript monitor inicializado para macOS")

    def _run_applescript(self, script: str) -> Optional[str]:
        """
        Executa um script AppleScript e retorna o resultado

        Args:
            script: Código AppleScript para executar

        Returns:
            Saída do script ou None se houver erro
        """
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                self.logger.error(f"AppleScript error: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            self.logger.error("AppleScript timeout")
            return None
        except Exception as e:
            self.logger.error(f"Erro ao executar AppleScript: {e}")
            return None

    def is_playing(self) -> bool:
        """Verifica se está tocando música"""
        script = '''
        tell application "Music"
            if it is running then
                return player state as string
            else
                return "stopped"
            end if
        end tell
        '''

        result = self._run_applescript(script)
        return result == "playing" if result else False

    def get_current_track(self) -> Optional[TrackInfo]:
        """
        Obtém informações da música atual

        Returns:
            TrackInfo ou None se nenhuma música estiver tocando
        """
        if not self.is_playing():
            return None

        # Script AppleScript para obter informações da música
        script = '''
        tell application "Music"
            if player state is playing then
                set trackName to name of current track
                set trackArtist to artist of current track
                set trackAlbum to album of current track
                set trackDuration to duration of current track
                set trackPosition to player position

                return trackName & "|" & trackArtist & "|" & trackAlbum & "|" & trackDuration & "|" & trackPosition
            else
                return ""
            end if
        end tell
        '''

        result = self._run_applescript(script)

        if not result:
            return None

        try:
            parts = result.split("|")
            if len(parts) >= 5:
                track_info = TrackInfo(
                    title=parts[0] or "Unknown",
                    artist=parts[1] or "Unknown Artist",
                    album=parts[2] or "Unknown Album",
                    artwork_url="embedded",  # Marcador para processar depois
                    duration=int(float(parts[3])),
                    position=int(float(parts[4]))
                )
                return track_info

        except Exception as e:
            self.logger.error(f"Erro ao parsear informações da música: {e}")

        return None

    def save_current_artwork(self, output_path: str) -> bool:
        """
        Salva a capa da música atual em um arquivo

        Args:
            output_path: Caminho para salvar a imagem

        Returns:
            True se salvou com sucesso, False caso contrário
        """
        # AppleScript para salvar a artwork
        script = f'''
        tell application "Music"
            if player state is playing then
                try
                    set currentArtwork to artwork 1 of current track
                    set artworkData to data of currentArtwork

                    set theFile to open for access POSIX file "{output_path}" with write permission
                    write artworkData to theFile
                    close access theFile

                    return "success"
                on error errMsg
                    try
                        close access POSIX file "{output_path}"
                    end try
                    return "error: " & errMsg
                end try
            else
                return "not playing"
            end if
        end tell
        '''

        result = self._run_applescript(script)

        if result == "success":
            return True
        else:
            self.logger.debug(f"Não foi possível salvar artwork: {result}")
            return False

    def get_player_info(self) -> Dict:
        """Retorna informações gerais do player"""
        try:
            track = self.get_current_track()

            # Obter volume
            volume_script = '''
            tell application "Music"
                return sound volume
            end tell
            '''
            volume_result = self._run_applescript(volume_script)
            volume = int(volume_result) if volume_result else 0

            return {
                "is_playing": self.is_playing(),
                "current_track": track.__dict__ if track else None,
                "volume": volume
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
    import time

    logging.basicConfig(level=logging.DEBUG)

    try:
        monitor = AppleMusicMonitorMacOS()

        print("Monitorando Apple Music no macOS... (Ctrl+C para sair)")
        print("Toque uma música no Apple Music para testar!\n")

        while True:
            track = monitor.get_current_track()

            if track:
                print(f"\n🎵 Tocando agora:")
                print(f"   Título: {track.title}")
                print(f"   Artista: {track.artist}")
                print(f"   Álbum: {track.album}")
                print(f"   Duração: {track.duration}s")
                print(f"   Posição: {track.position}s")

                # Testa salvar artwork
                if monitor.save_current_artwork("/tmp/test_artwork.jpg"):
                    print(f"   ✅ Artwork salva em /tmp/test_artwork.jpg")
                else:
                    print(f"   ⚠️  Não foi possível salvar artwork")
            else:
                print("\n⏸️  Nenhuma música tocando")

            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\nEncerrando...")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
