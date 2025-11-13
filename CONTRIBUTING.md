# 🤝 Guia de Contribuição

Obrigado por considerar contribuir com o Apple Music to iCUE LCD! Este documento fornece diretrizes para contribuir com o projeto.

## 📋 Código de Conduta

Este projeto adere a um código de conduta. Ao participar, você concorda em manter um ambiente respeitoso e acolhedor para todos.

## 🚀 Como Contribuir

### Reportando Bugs

Se você encontrou um bug:

1. **Verifique** se já não existe uma issue aberta sobre o problema
2. **Crie uma nova issue** com:
   - Título claro e descritivo
   - Descrição detalhada do problema
   - Passos para reproduzir
   - Comportamento esperado vs. atual
   - Screenshots (se aplicável)
   - Informações do sistema:
     - Versão do Python
     - Versão do Windows
     - Versão do iCUE
     - Logs relevantes

### Sugerindo Melhorias

Para sugerir uma melhoria:

1. **Abra uma issue** com a tag `enhancement`
2. **Descreva** a funcionalidade desejada
3. **Explique** por que seria útil
4. **Forneça exemplos** de uso

### Pull Requests

#### Antes de Começar

1. **Fork** o repositório
2. **Clone** seu fork localmente
3. **Crie uma branch** para sua feature:
   ```bash
   git checkout -b feature/minha-feature
   ```

#### Durante o Desenvolvimento

1. **Siga o estilo de código** do projeto
2. **Escreva testes** para novas funcionalidades
3. **Documente** mudanças no código
4. **Teste** localmente antes de commitar
5. **Commits claros** seguindo o padrão:
   ```
   tipo: descrição curta

   Descrição mais detalhada se necessário
   ```

   Tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

#### Submetendo o PR

1. **Push** para seu fork:
   ```bash
   git push origin feature/minha-feature
   ```

2. **Abra um Pull Request** com:
   - Título descritivo
   - Descrição das mudanças
   - Referência a issues relacionadas
   - Screenshots (se aplicável)

3. **Aguarde review** e responda a comentários

## 🎨 Padrões de Código

### Python Style Guide

- Siga [PEP 8](https://pep8.org/)
- Use type hints quando apropriado
- Docstrings em formato Google/NumPy
- Máximo 100 caracteres por linha

Exemplo:

```python
def process_image(image: Image.Image, size: Tuple[int, int]) -> Image.Image:
    """
    Processa uma imagem para o tamanho especificado.

    Args:
        image: Imagem PIL para processar
        size: Tupla (largura, altura) do tamanho alvo

    Returns:
        Imagem processada

    Raises:
        ValueError: Se o tamanho for inválido
    """
    if size[0] <= 0 or size[1] <= 0:
        raise ValueError("Tamanho deve ser positivo")

    return image.resize(size)
```

### Estrutura de Commits

```
tipo(escopo): descrição curta

Descrição mais detalhada do que foi mudado e por quê.

Closes #123
```

Exemplos:
- `feat(api): adiciona endpoint para configuração`
- `fix(monitor): corrige detecção de mudança de música`
- `docs(readme): atualiza instruções de instalação`

## 🧪 Testes

### Executando Testes

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Executar testes
pytest

# Com cobertura
pytest --cov=src tests/
```

### Escrevendo Testes

- Coloque testes em `tests/`
- Nomeie arquivos como `test_*.py`
- Use fixtures do pytest
- Mock dependências externas (iCUE, iTunes)

Exemplo:

```python
import pytest
from unittest.mock import Mock, patch
from src.apple_music_monitor import AppleMusicMonitor

def test_get_current_track():
    with patch('win32com.client.Dispatch') as mock_itunes:
        # Setup mock
        mock_itunes.return_value.CurrentTrack.Name = "Test Song"

        # Test
        monitor = AppleMusicMonitor()
        track = monitor.get_current_track()

        # Assert
        assert track.title == "Test Song"
```

## 📝 Documentação

### Atualizando Documentação

- README.md: Funcionalidades principais
- INSTALL.md: Guia de instalação
- CHANGELOG.md: Mudanças de versão
- Docstrings: Documentação inline

### Adicionando Exemplos

Exemplos são muito bem-vindos! Adicione em:
- `examples/`: Scripts de exemplo
- README.md: Exemplos de uso
- Docstrings: Exemplos inline

## 🏗️ Estrutura do Projeto

```
icue-applemusic/
├── src/              # Código fonte
│   ├── __init__.py
│   ├── main.py       # Aplicação principal
│   ├── api.py        # API REST
│   └── ...
├── tests/            # Testes
├── docs/             # Documentação adicional
├── examples/         # Exemplos de uso
└── scripts/          # Scripts auxiliares
```

## 🔍 Revisão de Código

Critérios para aprovação:

- ✅ Código funcional e testado
- ✅ Testes passando
- ✅ Documentação atualizada
- ✅ Estilo de código consistente
- ✅ Sem regressões
- ✅ Performance aceitável

## 🎯 Áreas Prioritárias

Contribuições são especialmente bem-vindas em:

1. **Suporte a mais dispositivos** Corsair
2. **Interface web** para configuração
3. **Testes automatizados** mais abrangentes
4. **Documentação** e exemplos
5. **Performance** e otimizações
6. **Suporte a outros players** de música

## 💬 Comunicação

- **Issues**: Para bugs e sugestões
- **Discussions**: Para perguntas e ideias
- **Pull Requests**: Para contribuições de código

## 📜 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença MIT do projeto.

---

Obrigado por contribuir! 🎵🎨
