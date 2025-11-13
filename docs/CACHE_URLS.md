# 📍 Cache Manual de URLs do Apple Music

Para álbuns muito recentes que ainda não foram indexados pela iTunes Search API, você pode adicionar as URLs manualmente.

## Como Funciona

O sistema tenta obter a URL do Apple Music nesta ordem:

1. **Cache Manual** (`apple_music_urls.json`) - URLs adicionadas por você
2. **iTunes Search API** - Busca automática
3. **Fallback** - Imagem estática de menor qualidade

## Quando Usar

Você verá esta mensagem nos logs quando um álbum não for encontrado:

```
⚠️  Álbum não encontrado na iTunes API: ROSALÍA - LUX
💡 Dica: Adicione ao cache manualmente:
   Arquivo: /path/to/apple_music_urls.json
   Chave: "rosalía|lux"
   Exemplo: "rosalía|lux": "https://music.apple.com/..."
```

## Como Adicionar URLs Manualmente

### 1. Encontre a URL do Álbum

Abra o Apple Music no navegador e busque o álbum:

```
https://music.apple.com/br/album/lux/1848167516
```

### 2. Edite o Arquivo `apple_music_urls.json`

```json
{
  "_comment": "Cache manual de URLs do Apple Music",
  "_format": "artist|album (lowercase) -> apple music url",

  "rosalía|lux": "https://music.apple.com/br/album/lux/1848167516",
  "artista|álbum": "https://music.apple.com/br/album/nome/id"
}
```

**Importante:**
- A chave deve ser `"artista|álbum"` em **lowercase**
- Use exatamente como aparece no Apple Music
- Caracteres especiais (á, é, í, etc.) devem ser mantidos

### 3. Teste

```bash
./test_macos.sh
```

Você verá:

```
📍 URL encontrada no cache manual: https://music.apple.com/br/album/lux/1848167516
🎬✨ CAPA ANIMADA salva em: /tmp/test_artwork.mov
```

## Exemplos

### Álbum Recente

```json
{
  "rosalía|lux": "https://music.apple.com/br/album/lux/1848167516"
}
```

### Múltiplos Álbuns

```json
{
  "rosalía|lux": "https://music.apple.com/br/album/lux/1848167516",
  "the weeknd|dawn fm": "https://music.apple.com/us/album/dawn-fm/1606933945",
  "dua lipa|future nostalgia": "https://music.apple.com/us/album/future-nostalgia/1499692231"
}
```

### Com Caracteres Especiais

```json
{
  "beyoncé|renaissance": "https://music.apple.com/us/album/renaissance/1630005298",
  "anitta|versions of me": "https://music.apple.com/us/album/versions-of-me/1613558589"
}
```

## Dicas

### Como Encontrar a URL no Navegador

1. Abra [music.apple.com](https://music.apple.com)
2. Busque pelo álbum
3. Clique no álbum
4. Copie a URL da barra de endereço

### Formato da URL

```
https://music.apple.com/{country}/album/{album-name}/{album-id}
```

Exemplo:
```
https://music.apple.com/br/album/lux/1848167516
                        ^^        ^^^  ^^^^^^^^^^
                       país      nome     ID
```

### Regiões Diferentes

A URL pode variar por país:

- Brasil: `https://music.apple.com/br/album/...`
- EUA: `https://music.apple.com/us/album/...`
- Portugal: `https://music.apple.com/pt/album/...`

A API playlist-precis aceita URLs de qualquer região.

## Troubleshooting

### "Chave não encontrada no cache"

Verifique se:
- A chave está em **lowercase**
- Não há espaços extras
- Os caracteres especiais estão corretos

### "Erro ao ler cache"

- Verifique a sintaxe JSON (vírgulas, aspas)
- Use um validador JSON online
- Confira se há vírgula após o último item (não deve ter)

### "URL não retorna capa animada"

Nem todos os álbuns têm capa animada. A API tentará e fará fallback para estática se necessário.

## Benefícios

✅ **Funciona para lançamentos de hoje** - Adicione imediatamente
✅ **Garante álbum correto** - Evita matches errados da API
✅ **Prioriza capa animada** - Se o álbum tiver, será baixada
✅ **Simples e rápido** - Apenas edite um JSON

---

**💡 Após adicionar URLs, o sistema as usará automaticamente na próxima execução!**
