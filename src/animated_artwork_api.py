"""
Cliente para API de capas animadas do Apple Music
Usa a API playlist-precis para obter vídeos animados das capas
"""
import logging
import requests
from typing import Optional


class AnimatedArtworkAPI:
    """
    Cliente para obter capas animadas via API playlist-precis
    """

    API_URL = "https://clients.dodoapps.io/playlist-precis/playlist-artwork.php"

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_animated_artwork_url(self, apple_music_url: str) -> Optional[str]:
        """
        Obtém a URL da capa animada via API

        Args:
            apple_music_url: URL do Apple Music (formato: https://music.apple.com/br/album/...)

        Returns:
            URL do vídeo animado ou None se não disponível
        """
        try:
            self.logger.info(f"Buscando capa animada via API para: {apple_music_url}")

            # Prepara o form data
            form_data = {
                'url': apple_music_url,
                'animation': 'true'
            }

            # Faz o POST
            response = requests.post(
                self.API_URL,
                data=form_data,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()

                # Verifica se tem a URL animada
                animated_url = data.get('animatedUrl')

                if animated_url:
                    self.logger.info(f"✨ Capa animada encontrada: {animated_url}")
                    return animated_url
                else:
                    self.logger.debug(f"Resposta não contém animatedUrl: {data}")
                    return None
            else:
                self.logger.warning(f"API retornou status {response.status_code}")
                return None

        except Exception as e:
            self.logger.error(f"Erro ao buscar capa animada: {e}")
            return None

    def download_animated_artwork(self, animated_url: str, output_path: str) -> bool:
        """
        Baixa a capa animada

        Args:
            animated_url: URL do vídeo animado
            output_path: Caminho para salvar

        Returns:
            True se baixou com sucesso
        """
        try:
            self.logger.info(f"Baixando capa animada de: {animated_url}")

            response = requests.get(animated_url, timeout=30, stream=True)

            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                self.logger.info(f"✅ Capa animada salva em: {output_path}")
                return True
            else:
                self.logger.error(f"Erro ao baixar: HTTP {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"Erro ao baixar capa animada: {e}")
            return False


if __name__ == "__main__":
    # Teste da API
    logging.basicConfig(level=logging.DEBUG)

    api = AnimatedArtworkAPI()

    # Teste com o álbum LUX da ROSALÍA
    test_url = "https://music.apple.com/br/album/lux/1848167516"

    animated_url = api.get_animated_artwork_url(test_url)

    if animated_url:
        print(f"✅ URL da capa animada: {animated_url}")

        # Testa o download
        if api.download_animated_artwork(animated_url, "/tmp/test_animated.mov"):
            print("✅ Capa animada baixada com sucesso!")
            print("   Abra com: open /tmp/test_animated.mov")
    else:
        print("❌ Não foi possível obter a capa animada")
