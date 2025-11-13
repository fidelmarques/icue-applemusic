# 🎨 Capas Animadas do Apple Music

Guia sobre como o sistema detecta e prioriza capas animadas.

## O que são Capas Animadas?

Apple Music Animated Cover Art são capas de álbum que se movem/animam, criando uma experiência visual mais rica. Nem todas as músicas têm capas animadas - é um recurso disponível principalmente em lançamentos recentes.

## Como o Sistema Detecta

O sistema usa duas estratégias:

### 1. Contagem de Artworks
```python
artwork_count = monitor.get_artwork_count()

if artwork_count > 1:
    # Provavelmente é uma capa animada!
    # Múltiplas artworks = múltiplos frames
```

**Músicas com capa animada geralmente têm:**
- 30-60 artworks (frames da animação)
- Cada artwork é um frame diferente

**Músicas com capa estática têm:**
- Apenas 1 artwork

### 2. Formato da Artwork
```python
# Verifica se é formato animado (GIF, MOV, APNG, etc)
is_animated = monitor.has_animated_artwork()
```

## Priorização

O sistema **sempre prioriza capas animadas**:

```python
# Por padrão, prefer_animated=True
monitor.save_current_artwork(output_path, prefer_animated=True)
```

Se uma música tem capa animada:
1. ✨ Detecta automaticamente
2. 📁 Salva múltiplos frames
3. 🖼️ Usa o primeiro frame como principal
4. 🔄 Pode criar loop de animação

## Testando

### Teste Rápido
```bash
./test_animated_artwork.sh
```

### Verificar Manualmente
```bash
# Toque uma música no Apple Music
# Depois execute:
python3 -c "
from src.apple_music_monitor_macos import AppleMusicMonitorMacOS
import logging
logging.basicConfig(level=logging.INFO)

monitor = AppleMusicMonitorMacOS()
count = monitor.get_artwork_count()
is_animated = monitor.has_animated_artwork()

print(f'Artworks: {count}')
print(f'Animada: {is_animated}')
"
```

## Exemplos

### Capa Estática
```
🎵 Tocando agora:
   Título: Bohemian Rhapsody
   Artista: Queen
   Álbum: A Night at the Opera
   🖼️  Capa estática (1 artwork)
   ✅ Artwork salva
```

### Capa Animada
```
🎵 Tocando agora:
   Título: [música recente]
   Artista: [artista]
   Álbum: [álbum]
   ✨ CAPA ANIMADA detectada! (45 frames)
   ✅ Artwork salva
   📁 Frames salvos: /tmp/test_artwork_frame*.jpg
```

## Processamento

Quando detecta capa animada:

1. **Salva frames-chave:**
   ```
   /tmp/test_artwork.jpg          (frame principal)
   /tmp/test_artwork_frame1.jpg   (primeiro frame)
   /tmp/test_artwork_frame45.jpg  (último frame)
   ```

2. **Logs informativos:**
   ```
   INFO: Detectada capa animada: 45 frames
   INFO: Salvando capa animada com 45 frames
   INFO: ✨ Capa ANIMADA salva (45 frames disponíveis)
   ```

## Como Encontrar Músicas com Capas Animadas

No Apple Music:

1. **Procure por "Spatial Audio" ou "Apple Music Animated"**
2. **Álbuns recentes de artistas populares**
3. **Lançamentos exclusivos do Apple Music**
4. **Playlists "New Music Daily"**

Exemplos de artistas com capas animadas:
- The Weeknd
- Dua Lipa
- Billie Eilish
- Travis Scott
- Lançamentos recentes de 2024/2025

## Limitações

### No macOS
- ✅ Detecta capas animadas
- ✅ Salva múltiplos frames
- ⚠️ Não cria GIF animado automaticamente (ainda)
- ⚠️ Display físico requer Windows + hardware

### Futuras Melhorias

Planejado:
- [ ] Criar GIF animado a partir dos frames
- [ ] Loop contínuo no LCD
- [ ] Ajustar FPS da animação
- [ ] Cache de animações
- [ ] Suporte a vídeo (MOV)

## API

### Verificar se tem capa animada
```python
from src.apple_music_monitor_macos import AppleMusicMonitorMacOS

monitor = AppleMusicMonitorMacOS()

# Número de frames
count = monitor.get_artwork_count()
print(f"Frames: {count}")

# É animada?
is_animated = monitor.has_animated_artwork()
print(f"Animada: {is_animated}")

# Salvar (prioriza animada automaticamente)
monitor.save_current_artwork("/tmp/artwork.jpg")
```

### Salvar frame específico
```python
# Salvar apenas frame 10
monitor._save_artwork_by_index("/tmp/frame10.jpg", 10)
```

### Salvar todos os frames
```python
count = monitor.get_artwork_count()

for i in range(1, count + 1):
    path = f"/tmp/frame_{i:03d}.jpg"
    monitor._save_artwork_by_index(path, i)
    print(f"Frame {i}/{count} salvo")
```

## Configuração

No `.env`:
```env
# Priorizar capas animadas (padrão: True)
PREFER_ANIMATED_ARTWORK=True

# Salvar todos os frames (pode ser lento)
SAVE_ALL_FRAMES=False

# Criar GIF a partir dos frames (futuro)
CREATE_ANIMATED_GIF=False
```

## Logs

Para ver detalhes da detecção:
```bash
# Executar com logs DEBUG
export LOG_LEVEL=DEBUG
./test_animated_artwork.sh
```

Exemplo de log:
```
DEBUG: AppleScript monitor inicializado para macOS
INFO: Detectada capa animada: 45 frames
INFO: Salvando capa animada com 45 frames
DEBUG: Frame 1 salvo: /tmp/test_artwork_frame1.jpg
DEBUG: Frame 45 salvo: /tmp/test_artwork_frame45.jpg
INFO: ✨ Capa ANIMADA salva (45 frames disponíveis)
```

## Troubleshooting

### "Sempre detecta como estática"
- Confirme que a música realmente tem capa animada
- Tente álbuns mais recentes
- Verifique se o Apple Music está atualizado

### "Frames não são salvos"
- Verifique permissões do diretório `/tmp`
- Logs podem mostrar erros específicos
- Tente com outro diretório

### "Muito lento para salvar todos os frames"
- Normal para 60+ frames
- Use `prefer_animated=False` para desabilitar
- Ou salve apenas frames-chave (padrão)

---

**🎨 Aproveite as capas animadas!** O sistema está otimizado para detectar e priorizar automaticamente.
