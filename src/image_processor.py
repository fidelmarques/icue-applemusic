"""
Processador de imagens com suporte a animações fade in/out
"""
import io
import logging
import os
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import requests


class ImageProcessor:
    """
    Processa imagens de capa de álbum para exibição no LCD
    """

    def __init__(self, target_size: Tuple[int, int] = (480, 480), cache_dir: str = "./cache"):
        """
        Args:
            target_size: Tamanho alvo do LCD (largura, altura)
            cache_dir: Diretório para cache de imagens
        """
        self.target_size = target_size
        self.cache_dir = cache_dir
        self.logger = logging.getLogger(__name__)

        # Cria diretório de cache se não existir
        os.makedirs(cache_dir, exist_ok=True)

    def download_image(self, url: str) -> Optional[Image.Image]:
        """
        Baixa imagem de uma URL

        Args:
            url: URL da imagem

        Returns:
            Objeto PIL Image ou None se falhar
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            image = Image.open(io.BytesIO(response.content))
            return image
        except Exception as e:
            self.logger.error(f"Erro ao baixar imagem de {url}: {e}")
            return None

    def load_from_file(self, file_path: str) -> Optional[Image.Image]:
        """
        Carrega imagem de um arquivo

        Args:
            file_path: Caminho do arquivo

        Returns:
            Objeto PIL Image ou None se falhar
        """
        try:
            if not os.path.exists(file_path):
                return None

            image = Image.open(file_path)
            return image
        except Exception as e:
            self.logger.error(f"Erro ao carregar imagem de {file_path}: {e}")
            return None

    def resize_and_crop(self, image: Image.Image) -> Image.Image:
        """
        Redimensiona e corta a imagem para o tamanho alvo mantendo proporção

        Args:
            image: Imagem original

        Returns:
            Imagem processada
        """
        # Converte para RGB se necessário
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Calcula o crop para manter proporção
        img_width, img_height = image.size
        target_width, target_height = self.target_size

        # Calcula a razão de aspecto
        img_ratio = img_width / img_height
        target_ratio = target_width / target_height

        if img_ratio > target_ratio:
            # Imagem é mais larga, corta dos lados
            new_width = int(img_height * target_ratio)
            left = (img_width - new_width) // 2
            image = image.crop((left, 0, left + new_width, img_height))
        else:
            # Imagem é mais alta, corta de cima/baixo
            new_height = int(img_width / target_ratio)
            top = (img_height - new_height) // 2
            image = image.crop((0, top, img_width, top + new_height))

        # Redimensiona para o tamanho alvo
        image = image.resize(self.target_size, Image.Resampling.LANCZOS)

        return image

    def apply_fade(self, image: Image.Image, alpha: float) -> Image.Image:
        """
        Aplica efeito de fade (transparência) na imagem

        Args:
            image: Imagem original
            alpha: Nível de opacidade (0.0 = transparente, 1.0 = opaco)

        Returns:
            Imagem com fade aplicado
        """
        # Garante que alpha está entre 0 e 1
        alpha = max(0.0, min(1.0, alpha))

        # Converte para RGBA se necessário
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Ajusta o canal alpha
        enhancer = ImageEnhance.Brightness(image)
        faded = enhancer.enhance(alpha)

        return faded

    def blend_images(self, img1: Image.Image, img2: Image.Image, alpha: float) -> Image.Image:
        """
        Faz blend (transição) entre duas imagens

        Args:
            img1: Primeira imagem
            img2: Segunda imagem
            alpha: Fator de blend (0.0 = img1, 1.0 = img2)

        Returns:
            Imagem resultante do blend
        """
        # Garante que alpha está entre 0 e 1
        alpha = max(0.0, min(1.0, alpha))

        # Garante que as imagens têm o mesmo tamanho e modo
        if img1.size != img2.size:
            img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)

        if img1.mode != img2.mode:
            if img1.mode == 'RGB':
                img2 = img2.convert('RGB')
            elif img1.mode == 'RGBA':
                img2 = img2.convert('RGBA')

        # Faz o blend
        return Image.blend(img1, img2, alpha)

    def add_overlay_info(self, image: Image.Image, title: str, artist: str) -> Image.Image:
        """
        Adiciona overlay com informações da música (opcional)

        Args:
            image: Imagem base
            title: Título da música
            artist: Nome do artista

        Returns:
            Imagem com overlay
        """
        # Cria uma cópia para não modificar a original
        img_copy = image.copy()

        # TODO: Implementar overlay com texto
        # Isso requer uma fonte TrueType, que pode não estar disponível
        # Por enquanto, retorna a imagem sem modificações

        return img_copy

    def create_placeholder(self, text: str = "🎵") -> Image.Image:
        """
        Cria uma imagem placeholder quando não há capa disponível

        Args:
            text: Texto para exibir

        Returns:
            Imagem placeholder
        """
        # Cria imagem com gradiente
        image = Image.new('RGB', self.target_size, color=(20, 20, 30))

        draw = ImageDraw.Draw(image)

        # Desenha um círculo no centro
        center_x, center_y = self.target_size[0] // 2, self.target_size[1] // 2
        radius = min(self.target_size) // 3

        # Gradiente radial simulado com círculos concêntricos
        for i in range(radius, 0, -5):
            color_val = int(255 * (i / radius) * 0.3)
            color = (color_val, color_val // 2, color_val // 2)
            draw.ellipse(
                [center_x - i, center_y - i, center_x + i, center_y + i],
                fill=color
            )

        return image

    def process_artwork(self, source, track_info=None) -> Optional[Image.Image]:
        """
        Processa uma capa de álbum completa

        Args:
            source: URL, caminho de arquivo ou objeto Image
            track_info: Informações da música (opcional)

        Returns:
            Imagem processada pronta para exibição
        """
        try:
            # Carrega a imagem
            if isinstance(source, str):
                if source.startswith('http'):
                    image = self.download_image(source)
                else:
                    image = self.load_from_file(source)
            elif isinstance(source, Image.Image):
                image = source
            else:
                image = None

            if image is None:
                self.logger.warning("Não foi possível carregar imagem, usando placeholder")
                image = self.create_placeholder()

            # Redimensiona e corta
            image = self.resize_and_crop(image)

            # Aplica filtro de nitidez leve
            image = image.filter(ImageFilter.SHARPEN)

            return image

        except Exception as e:
            self.logger.error(f"Erro ao processar artwork: {e}")
            return self.create_placeholder()

    def save_to_cache(self, image: Image.Image, cache_key: str) -> str:
        """
        Salva imagem no cache

        Args:
            image: Imagem para salvar
            cache_key: Chave única para identificar a imagem

        Returns:
            Caminho do arquivo salvo
        """
        # Remove caracteres inválidos do nome do arquivo
        safe_key = "".join(c for c in cache_key if c.isalnum() or c in (' ', '-', '_')).rstrip()
        cache_path = os.path.join(self.cache_dir, f"{safe_key}.png")

        try:
            image.save(cache_path, 'PNG')
            return cache_path
        except Exception as e:
            self.logger.error(f"Erro ao salvar no cache: {e}")
            return ""


if __name__ == "__main__":
    # Teste do processador
    logging.basicConfig(level=logging.DEBUG)

    processor = ImageProcessor()

    # Cria um placeholder
    placeholder = processor.create_placeholder()
    placeholder.show()

    print("✅ Processador de imagens funcionando!")
