# Ferramenta de Comparação de Imagens para QA

Esta ferramenta permite comparar duas imagens automaticamente e identificar diferenças visuais de forma gráfica e estatística. Foi desenvolvida com foco em tarefas de **Quality Assurance (QA)** de interfaces gráficas, como menus ou ecrãs de aplicações/jogos.

## Funcionalidades

- Suporte a múltiplos métodos de comparação:
  - Diferença Absoluta de Pixels (AbsDiff)
  - Structural Similarity Index (SSIM)
  - Comparação de Histogramas
- Geração automática de relatórios em PDF
- Métricas de comparação:
  - Número de diferenças visuais
  - Percentagem de pixels alterados
  - Tempo de execução por método
- Destaque visual das zonas alteradas (overlay transparente)
- Observações automáticas com base nas diferenças detetadas

## Estrutura do Projeto

```
comparador-imagens/
├── historico/             # Arquivo de relatórios anteriores
├── imagens/
│   ├── referencia/        # Imagens originais a usar como base
│   └── teste/             # Imagens de teste a comparar
├── output/
│   └── relatorio.py       # Geração de relatórios PDF
├── processamento/
│   └── analises.py        # Métodos de comparação implementados
├── relatorios/            # Relatórios mais recentes gerados automaticamente
├── gerar_imagens.py       # Geração de imagens de teste artificiais
├── main.py                # Ponto de entrada do sistema
└── README.md              # Este ficheiro
```

## Requisitos

- Python 3.13+
- Bibliotecas Python:
  - `opencv-python`
  - `numpy`
  - `reportlab`
  - `scikit-image`

Instalação de dependências:
```bash
pip install opencv-python numpy reportlab scikit-image
```

## Como Usar

1. **Colocar duas imagens com o mesmo nome** nas seguintes pastas:
   - `imagens/referencia/`
   - `imagens/teste/`

2. **Escolher a imagem a comparar** no ficheiro `main.py`, alterando o valor da variável `IMG_NOME`:

```python
# Ficheiro: main.py

# Nome do ficheiro a comparar (deve existir em ambas as pastas)
# Exemplos disponíveis: menu, menu_igual, meme, resol_dif, em_falta
IMG_NOME = "menu.png"
```

3. **Executar o programa principal** no terminal:

```bash
python main.py
```

4. O sistema irá:
   - Comparar as imagens com os métodos configurados
   - Gerar um relatório em PDF na pasta `relatorios/`
   - Guardar a imagem com diferenças destacadas (se aplicável)

## Exemplos

- Comparações entre capturas de ecrã reais do jogo **8BallPool** (Miniclip)
- Testes com imagens artificiais criadas com `gerar_imagens.py`
- Casos com:
  - Imagens idênticas (0% diferença)
  - Pequenas alterações visuais (mesmo menu, estado diferente)
  - Imagens completamente distintas (menu vs meme)

## Observações

- As imagens a comparar **devem ter a mesma resolução**.
- Os relatórios anteriores podem ser encontrados na pasta `historico/`.

## Licença

Este projeto foi desenvolvido em contexto académico e não possui fins comerciais.