import cv2
import os
import time
import uuid

# Importação de funções do módulo de geração de relatórios
from output.relatorio import guardar_imagem_resultado, gerar_relatorio_pdf

# Importação de funções do módulo de análise de diferenças
from processamento.analises import analisar_diferencas

# Definir o método de análise: "absdiff", "histograma" ou "ssim"
metodo_analise = "absdiff"

# Definir caminhos das imagens de referência e de teste
IMG_NOME = "menu.png"
IMG_REFERENCIA = os.path.join("imagens", "referencia", IMG_NOME)
IMG_TESTE = os.path.join("imagens", "teste", IMG_NOME)

# Carregar imagens
img_ref = cv2.imread(IMG_REFERENCIA)
img_teste = cv2.imread(IMG_TESTE)

# Verifica se ambas as imagens foram carregadas corretamente
if img_ref is None:
    print(f"❌ Imagem de referência não encontrada: {IMG_REFERENCIA}")
    exit(1)

if img_teste is None:
    print(f"❌ Imagem de teste não encontrada: {IMG_TESTE}")
    exit(1)

# Verifica se as imagens têm o mesmo tamanho
if img_ref.shape != img_teste.shape:
    print("❌ As imagens têm tamanhos diferentes e não podem ser comparadas diretamente.")
    exit(1)

# Gera identificador único
id_relatorio = str(uuid.uuid4())[:8]

# Inicia contagem do tempo
inicio = time.time()

# Executa a análise selecionada
img_resultado, tipo_analise, metricas = analisar_diferencas(img_ref, img_teste, metodo = metodo_analise)

# Calcula tempo de execução
duracao = time.time() - inicio

# Guarda a imagem de resultado
caminho_resultado = None
if metodo_analise in ["absdiff", "ssim"]:
    caminho_resultado = guardar_imagem_resultado(img_resultado, metodo = metodo_analise, identificador = id_relatorio)

# Cópia completa das métricas para uso em observações automáticas
extra_metricas = metricas.copy()

# Gera o relatório PDF; a imagem de resultado só é obrigatória para métodos com comparação visual (absdiff e ssim)
if caminho_resultado or metodo_analise == "histograma":
    gerar_relatorio_pdf(
        img_ref_path = IMG_REFERENCIA,
        img_teste_path = IMG_TESTE,
        img_resultado_path = caminho_resultado,
        num_diferencas = metricas.get("num_diferencas"),
        total_pixels = metricas.get("total_pixels"),
        pixels_diferentes = metricas.get("pixels_diferentes"),
        percentagem_diferenca = metricas.get("percentagem_diferenca"),
        tipo_analise = tipo_analise,
        metodo = metodo_analise,
        identificador = id_relatorio,
        duracao = duracao,
        extra_metricas = extra_metricas
    )
else:
    print("⚠️ A imagem de resultado não foi guardada. O relatório PDF não será gerado.")

# Mostra a imagem de resultado
cv2.imshow("Diferenças Detetadas", img_resultado)
cv2.waitKey(0)
cv2.destroyAllWindows()