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
    year: Optional[int] = None

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
                set trackYear to year of current track

                -- Tenta obter a URL do Apple Music
                set appleURL to ""
                try
                    set appleURL to (get persistent ID of current track) as string
                end try

                return trackName & "|" & trackArtist & "|" & trackAlbum & "|" & trackDuration & "|" & trackPosition & "|" & appleURL & "|" & trackYear
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

                # URL do Apple Music e ano (se disponíveis)
                apple_music_url = parts[5] if len(parts) > 5 and parts[5] else None
                year = parts[6] if len(parts) > 6 and parts[6] else None

                track_info = TrackInfo(
                    title=parts[0] or "Unknown",
                    artist=parts[1] or "Unknown Artist",
                    album=parts[2] or "Unknown Album",
                    artwork_url=apple_music_url,  # Persistente ID
                    duration=int(float(duration_str)),
                    position=int(float(position_str))
                )

                # Guarda o ano para usar na busca depois
                if year and year != "0":
                    track_info.year = int(year)

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
                    set artCount to count of artworks of current track
                    if artCount is missing value then
                        return 0
                    else
                        return artCount
                    end if
                on error errMsg
                    log "Erro ao contar artworks: " & errMsg
                    return 0
                end try
            else
                return 0
            end if
        end tell
        '''

        result = self._run_applescript(script)
        try:
            count = int(result) if result and result != "" else 0
            self.logger.debug(f"Artwork count: {count}")
            return count
        except Exception as e:
            self.logger.debug(f"Erro ao parsear contagem de artworks: {e}, resultado: '{result}'")
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
        import os
        import tempfile

        # Para Apple Music streaming, usamos uma abordagem diferente
        # Vamos construir a URL da capa baseado nas informações da música
        script_get_info = '''
        tell application "Music"
            if player state is playing then
                try
                    set currentTrack to current track

                    -- Primeiro, tenta salvar artwork diretamente (funciona para músicas locais)
                    try
                        if (count of artworks of currentTrack) > 0 then
                            return "has_artwork"
                        end if
                    end try

                    -- Para streaming, tenta obter informações para construir URL
                    try
                        set albumName to album of currentTrack
                        set artistName to artist of currentTrack

                        -- Tenta obter URL do Apple Music
                        set storeURL to ""
                        try
                            -- Usa as propriedades disponíveis no Music.app
                            set storeURL to (location of currentTrack) as string
                        end try

                        if storeURL is not "" then
                            return "streaming|" & albumName & "|" & artistName & "|" & storeURL
                        else
                            return "streaming|" & albumName & "|" & artistName & "|"
                        end if
                    end try

                    return "no_info"
                on error errMsg
                    return "error: " & errMsg
                end try
            else
                return "not playing"
            end if
        end tell
        '''

        info_result = self._run_applescript(script_get_info)

        # Método 1: Artwork embarcada (músicas locais)
        if info_result == "has_artwork":
            script_save = f'''
            tell application "Music"
                if player state is playing then
                    try
                        set currentArtwork to artwork 1 of current track
                        set artworkData to data of currentArtwork

                        set theFile to open for access POSIX file "{output_path}" with write permission
                        set eof of theFile to 0
                        write artworkData to theFile
                        close access theFile

                        return "success"
                    on error errMsg
                        try
                            close access POSIX file "{output_path}"
                        end try
                        return "error: " & errMsg
                    end try
                end if
            end tell
            '''

            result = self._run_applescript(script_save)
            if result == "success":
                artwork_count = self.get_artwork_count()
                if artwork_count > 1:
                    self.logger.info(f"✨ Capa ANIMADA salva ({artwork_count} frames)")
                else:
                    self.logger.info("🖼️  Capa estática salva")
                return True

        # Método 2: Streaming - PRIORIZA API de capas animadas!
        elif info_result and info_result.startswith("streaming|"):
            parts = info_result.split("|")
            if len(parts) >= 3:
                album = parts[1]
                artist = parts[2]
                apple_music_url = parts[3] if len(parts) > 3 else None

                # Pega informações da música atual para melhorar a busca
                current_track = self.get_current_track()
                track_title = current_track.title if current_track else ""
                track_year = current_track.year if current_track and hasattr(current_track, 'year') else None

                # ESTRATÉGIA 1: API de Capas Animadas (PRIORIDADE MÁXIMA!)
                # Se não temos a URL do Apple Music, tentamos construir
                if prefer_animated:
                    self.logger.info(f"🎬 Tentando obter capa ANIMADA via API...")

                    try:
                        from animated_artwork_api import AnimatedArtworkAPI
                        import urllib.parse
                        import requests

                        # Se não temos apple_music_url, constrói manualmente
                        if not apple_music_url or apple_music_url == "":
                            self.logger.info("Construindo URL do Apple Music...")

                            # Usa a API do Apple Music Catalog Search (sem autenticação)
                            # Formato: https://music.apple.com/search?term=query
                            search_term = f"{artist} {album}"
                            search_url = f"https://music.apple.com/search?term={urllib.parse.quote(search_term)}"

                            self.logger.info(f"URL de busca: {search_url}")

                            # A API playlist-precis pode aceitar a URL de busca diretamente!
                            # Vamos tentar com ela
                            apple_music_url = search_url

                        # Se conseguimos a URL do Apple Music, tenta obter capa animada
                        if apple_music_url and apple_music_url != "":
                            api = AnimatedArtworkAPI()
                            animated_url = api.get_animated_artwork_url(apple_music_url)

                            if animated_url:
                                # Determina a extensão do arquivo animado
                                animated_path = output_path.replace('.jpg', '.mov')

                                if api.download_animated_artwork(animated_url, animated_path):
                                    self.logger.info(f"🎬✨ CAPA ANIMADA salva em: {animated_path}")

                                    # Também salva um frame estático como fallback
                                    self._extract_frame_from_video(animated_path, output_path)

                                    return True
                        else:
                            self.logger.debug("Não foi possível obter URL do Apple Music")

                    except Exception as e:
                        self.logger.debug(f"Erro ao obter capa animada: {e}")
                        self.logger.info("⏩ Fallback para busca estática...")

                # ESTRATÉGIA 2: iTunes Search API (fallback para imagem estática)
                import urllib.parse
                import requests

                # Tenta várias estratégias de busca
                search_strategies = [
                    # 1. Artista + Álbum
                    (f"{artist} {album}", "artista + álbum"),
                    # 2. Apenas artista (pega álbum mais recente)
                    (artist, "apenas artista"),
                    # 3. Artista sem caracteres especiais
                    (artist.replace("Í", "I").replace("Á", "A"), "artista normalizado"),
                ]

                for search_term, strategy in search_strategies:
                    try:
                        self.logger.info(f"Busca via iTunes API ({strategy}): {search_term}")

                        query = urllib.parse.quote(search_term)
                        itunes_api_url = f"https://itunes.apple.com/search?term={query}&entity=album&limit=5"

                        response = requests.get(itunes_api_url, timeout=5)
                        if response.status_code == 200:
                            data = response.json()

                            self.logger.debug(f"API retornou {data.get('resultCount', 0)} resultados")

                            if data.get('resultCount', 0) > 0:
                                # Se buscou apenas artista, tenta encontrar o álbum correto
                                best_match = None

                                for result in data.get('results', []):
                                    result_album = result.get('collectionName', '').lower()
                                    result_artist = result.get('artistName', '').lower()

                                    # Prioriza match exato do álbum
                                    if album.lower() in result_album or result_album in album.lower():
                                        best_match = result
                                        self.logger.info(f"Match exato: {result_artist} - {result_album}")
                                        break

                                # Se não encontrou match exato, pega o primeiro resultado
                                if not best_match and data['results']:
                                    best_match = data['results'][0]
                                    self.logger.info(f"Usando primeiro resultado: {best_match.get('artistName')} - {best_match.get('collectionName')}")

                                if best_match:
                                    artwork_url = best_match.get('artworkUrl100', '')

                                    if artwork_url:
                                        # Aumenta a resolução para 3000x3000 (máximo disponível)
                                        artwork_url = artwork_url.replace('100x100bb.jpg', '3000x3000bb.jpg')

                                        self.logger.info(f"Baixando artwork: {artwork_url}")

                                        # Baixa a imagem
                                        img_response = requests.get(artwork_url, timeout=10)
                                        if img_response.status_code == 200:
                                            with open(output_path, 'wb') as f:
                                                f.write(img_response.content)

                                            self.logger.info(f"🖼️  Capa estática baixada via iTunes API ({strategy})")
                                            return True
                                        else:
                                            self.logger.debug(f"Erro ao baixar imagem: HTTP {img_response.status_code}")

                    except Exception as e:
                        self.logger.debug(f"Erro na estratégia '{strategy}': {e}")
                        continue

                self.logger.warning(f"Nenhuma estratégia de busca teve sucesso para: {artist} - {album}")

        # Método 3: Fallback - sem sucesso
        self.logger.warning("Não foi possível obter artwork - métodos disponíveis esgotados")
        return False

    def _extract_frame_from_video(self, video_path: str, output_path: str) -> bool:
        """
        Extrai um frame do vídeo para usar como thumbnail estático

        Args:
            video_path: Caminho do vídeo
            output_path: Caminho para salvar o frame

        Returns:
            True se extraiu com sucesso
        """
        try:
            # Usa ffmpeg se disponível
            import subprocess

            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vframes', '1',
                '-f', 'image2',
                '-y',
                output_path
            ]

            result = subprocess.run(cmd, capture_output=True, timeout=10)

            if result.returncode == 0:
                self.logger.info(f"Frame estático extraído: {output_path}")
                return True

        except Exception as e:
            self.logger.debug(f"Não foi possível extrair frame: {e}")

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
