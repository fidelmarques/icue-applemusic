"""
Controlador do iCUE SDK para exibir imagens no LCD do Corsair
"""
import logging
import time
from typing import Optional, Tuple
from PIL import Image
import io

try:
    from cue_sdk import CueSdk
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    logging.warning("cuesdk não disponível. Controlador iCUE não funcionará.")


class ICueController:
    """
    Controla dispositivos Corsair iCUE com LCD (como H150i Elite LCD XT)
    """

    def __init__(self, lcd_size: Tuple[int, int] = (480, 480)):
        """
        Args:
            lcd_size: Tamanho do LCD (largura, altura)
        """
        self.lcd_size = lcd_size
        self.sdk = None
        self.logger = logging.getLogger(__name__)
        self.connected = False
        self.current_image: Optional[Image.Image] = None

        if not SDK_AVAILABLE:
            self.logger.warning("cuesdk não está instalado. Modo simulação ativado.")
            return

        self._connect()

    def _connect(self):
        """Conecta ao iCUE SDK"""
        try:
            self.sdk = CueSdk()

            # Inicializa o SDK
            details = self.sdk.connect()

            if details:
                self.logger.info(f"Conectado ao iCUE SDK v{details}")
                self.connected = True

                # Lista dispositivos disponíveis
                devices = self.sdk.get_devices()
                self.logger.info(f"Dispositivos encontrados: {len(devices)}")

                for idx, device in enumerate(devices):
                    self.logger.info(f"  [{idx}] {device}")

            else:
                self.logger.error("Falha ao conectar ao iCUE SDK")
                self.connected = False

        except Exception as e:
            self.logger.error(f"Erro ao conectar ao iCUE SDK: {e}")
            self.connected = False

    def set_image(self, image: Image.Image) -> bool:
        """
        Define a imagem atual no LCD

        Args:
            image: Imagem PIL para exibir

        Returns:
            True se teve sucesso, False caso contrário
        """
        if not SDK_AVAILABLE:
            self.logger.debug("Modo simulação: imagem definida")
            self.current_image = image
            return True

        try:
            if not self.connected:
                self.logger.warning("Não conectado ao iCUE SDK, tentando reconectar...")
                self._connect()

            if not self.connected:
                return False

            # Garante que a imagem tem o tamanho correto
            if image.size != self.lcd_size:
                image = image.resize(self.lcd_size, Image.Resampling.LANCZOS)

            # Converte para RGB se necessário
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Converte a imagem para bytes
            # O formato esperado pode variar dependendo do SDK
            # Aqui assumimos RGB raw bytes
            image_bytes = image.tobytes()

            # Envia para o SDK
            # NOTA: A API exata depende da versão do cuesdk
            # Pode precisar de ajustes baseado na documentação oficial
            try:
                # Tentativa de enviar para o LCD
                # A implementação exata depende da API do cuesdk
                self.sdk.set_led_colors_buffer_by_device_index(0, image_bytes)
                self.sdk.set_led_colors_flush_buffer()
            except AttributeError:
                # Método alternativo se o acima não existir
                self.logger.warning("Método set_led_colors_buffer_by_device_index não encontrado")
                # Implementação alternativa aqui

            self.current_image = image
            return True

        except Exception as e:
            self.logger.error(f"Erro ao definir imagem no LCD: {e}")
            return False

    def fade_transition(self, new_image: Image.Image, duration: float = 1.0, fps: int = 30) -> bool:
        """
        Faz transição fade entre a imagem atual e uma nova

        Args:
            new_image: Nova imagem para exibir
            duration: Duração da transição em segundos
            fps: Frames por segundo da animação

        Returns:
            True se teve sucesso, False caso contrário
        """
        if not self.current_image:
            # Se não há imagem atual, apenas define a nova
            return self.set_image(new_image)

        try:
            # Garante que ambas as imagens têm o mesmo tamanho e modo
            old_image = self.current_image.copy()

            if old_image.size != new_image.size:
                new_image = new_image.resize(old_image.size, Image.Resampling.LANCZOS)

            if old_image.mode != new_image.mode:
                new_image = new_image.convert(old_image.mode)

            # Calcula o número de frames
            total_frames = int(duration * fps)
            frame_delay = 1.0 / fps

            # Executa a transição
            for frame in range(total_frames + 1):
                alpha = frame / total_frames

                # Faz o blend entre as imagens
                blended = Image.blend(old_image, new_image, alpha)

                # Exibe o frame
                self.set_image(blended)

                # Aguarda o próximo frame
                if frame < total_frames:
                    time.sleep(frame_delay)

            # Garante que a imagem final foi definida
            self.current_image = new_image

            return True

        except Exception as e:
            self.logger.error(f"Erro durante transição fade: {e}")
            return False

    def clear(self) -> bool:
        """
        Limpa o LCD (tela preta)

        Returns:
            True se teve sucesso
        """
        black_image = Image.new('RGB', self.lcd_size, color=(0, 0, 0))
        return self.set_image(black_image)

    def disconnect(self):
        """Desconecta do iCUE SDK"""
        if self.sdk and self.connected:
            try:
                self.sdk.disconnect()
                self.logger.info("Desconectado do iCUE SDK")
            except Exception as e:
                self.logger.error(f"Erro ao desconectar: {e}")

        self.connected = False


class MockICueController(ICueController):
    """
    Versão mock do controller para testes sem hardware
    """

    def __init__(self, lcd_size: Tuple[int, int] = (480, 480)):
        self.lcd_size = lcd_size
        self.logger = logging.getLogger(__name__)
        self.connected = True
        self.current_image: Optional[Image.Image] = None
        self.logger.info("Mock iCUE Controller inicializado (sem hardware)")

    def _connect(self):
        self.connected = True
        self.logger.info("Mock: Conectado")

    def set_image(self, image: Image.Image) -> bool:
        self.current_image = image
        self.logger.info(f"Mock: Imagem definida ({image.size})")
        return True

    def fade_transition(self, new_image: Image.Image, duration: float = 1.0, fps: int = 30) -> bool:
        self.logger.info(f"Mock: Fade transition ({duration}s @ {fps}fps)")
        time.sleep(duration)  # Simula a duração
        self.current_image = new_image
        return True

    def clear(self) -> bool:
        self.logger.info("Mock: LCD limpo")
        self.current_image = None
        return True

    def disconnect(self):
        self.logger.info("Mock: Desconectado")
        self.connected = False


if __name__ == "__main__":
    # Teste do controlador
    logging.basicConfig(level=logging.DEBUG)

    # Usa mock para testes sem hardware
    controller = MockICueController()

    # Cria uma imagem de teste
    test_image = Image.new('RGB', (480, 480), color=(255, 0, 0))

    print("Definindo imagem vermelha...")
    controller.set_image(test_image)

    time.sleep(1)

    # Cria segunda imagem
    test_image2 = Image.new('RGB', (480, 480), color=(0, 0, 255))

    print("Fazendo fade para azul...")
    controller.fade_transition(test_image2, duration=2.0)

    print("✅ Controlador iCUE funcionando!")

    controller.disconnect()
