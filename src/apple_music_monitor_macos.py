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
                # Substitui vírgula por ponto para locales diferentes
                duration_str = parts[3].replace(",", ".")
                position_str = parts[4].replace(",", ".")

                track_info = TrackInfo(
                    title=parts[0] or "Unknown",
                    artist=parts[1] or "Unknown Artist",
                    album=parts[2] or "Unknown Album",
                    artwork_url="embedded",  # Marcador para processar depois
                    duration=int(float(duration_str)),
                    position=int(float(position_str))
                )
                return track_info

        except Exception as e:
            self.logger.error(f"Erro ao parsear informações da música: {e}")

        return None

    def get_artwork_count(self) -> int:
        """
        Retorna o número de artworks disponíveis para a música atual
        (Músicas com capa animada geralmente têm múltiplas artworks)

        Returns:
            Número de artworks disponíveis
        """
        script = '''
        tell application "Music"
            if player state is playing then
                try
                    return count of artworks of current track
                on error
                    return 0
                end try
            else
                return 0
            end if
        end tell
        '''

        result = self._run_applescript(script)
        try:
            return int(result) if result else 0
        except:
            return 0

    def has_animated_artwork(self) -> bool:
        """
        Verifica se a música atual tem capa animada

        Capas animadas geralmente:
        - Têm múltiplas artworks (uma para cada frame)
        - Ou são formatos como MOV, GIF

        Returns:
            True se tem capa animada
        """
        artwork_count = self.get_artwork_count()

        # Se tem mais de 1 artwork, provavelmente é animada
        if artwork_count > 1:
            self.logger.info(f"Detectada capa animada: {artwork_count} frames")
            return True

        # Verifica o formato da artwork
        script = '''
        tell application "Music"
            if player state is playing then
                try
                    set currentArtwork to artwork 1 of current track
                    return format of currentArtwork as string
                on error
                    return "unknown"
                end try
            else
                return "unknown"
            end if
        end tell
        '''

        result = self._run_applescript(script)

        # Formatos animados conhecidos
        animated_formats = ["MOV", "GIF", "APNG", "WEBP"]
        is_animated = any(fmt.lower() in result.lower() for fmt in animated_formats)

        if is_animated:
            self.logger.info(f"Detectado formato animado: {result}")

        return is_animated

    def save_current_artwork(self, output_path: str, prefer_animated: bool = True) -> bool:
        """
        Salva a capa da música atual em um arquivo
        PRIORIZA capas animadas sobre estáticas!

        Args:
            output_path: Caminho para salvar a imagem
            prefer_animated: Se True, tenta salvar versão animada primeiro

        Returns:
            True se salvou com sucesso, False caso contrário
        """
        # Verifica se tem capa animada
        artwork_count = self.get_artwork_count()

        if prefer_animated and artwork_count > 1:
            # Tenta salvar todas as artworks (frames da animação)
            self.logger.info(f"Salvando capa animada com {artwork_count} frames")

            # Para animações, vamos salvar a primeira e última (para criar loop)
            # Você pode modificar isso para salvar todas
            for idx in [1, artwork_count]:
                frame_path = output_path.replace(".jpg", f"_frame{idx}.jpg")
                success = self._save_artwork_by_index(frame_path, idx)
                if idx == 1 and success:
                    # Copia o primeiro frame como o arquivo principal
                    import shutil
                    try:
                        shutil.copy(frame_path, output_path)
                    except:
                        pass

        # Salva a artwork principal (ou única se não for animada)
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
            # Log se é animada ou não
            if artwork_count > 1:
                self.logger.info(f"✨ Capa ANIMADA salva ({artwork_count} frames disponíveis)")
            else:
                self.logger.info("🖼️  Capa estática salva")
            return True
        else:
            self.logger.debug(f"Não foi possível salvar artwork: {result}")
            return False

    def _save_artwork_by_index(self, output_path: str, index: int) -> bool:
        """
        Salva uma artwork específica por índice (para animações)

        Args:
            output_path: Caminho para salvar
            index: Índice da artwork (1-based)

        Returns:
            True se salvou com sucesso
        """
        script = f'''
        tell application "Music"
            if player state is playing then
                try
                    set currentArtwork to artwork {index} of current track
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
        return result == "success"

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

                # Verifica se tem capa animada
                artwork_count = monitor.get_artwork_count()
                is_animated = monitor.has_animated_artwork()

                if is_animated or artwork_count > 1:
                    print(f"   ✨ CAPA ANIMADA detectada! ({artwork_count} frames)")
                else:
                    print(f"   🖼️  Capa estática ({artwork_count} artwork)")

                # Testa salvar artwork
                if monitor.save_current_artwork("/tmp/test_artwork.jpg"):
                    print(f"   ✅ Artwork salva em /tmp/test_artwork.jpg")

                    # Se tem frames adicionais, mostra
                    if artwork_count > 1:
                        print(f"   📁 Frames salvos: /tmp/test_artwork_frame*.jpg")
                else:
                    print(f"   ⚠️  Não foi possível salvar artwork")
            else:
                print("\n⏸️  Nenhuma música tocando")

            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\nEncerrando...")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
