import cv2
import os

# Importação de funções do módulo de geração de relatórios
from output.relatorio import guardar_imagem_resultado, gerar_relatorio_pdf

# Importação de funções do módulo de análise de diferenças
from comparador.analises import analisar_diferencas

# Definir o método de análise: "absdiff", "histograma" ou "ssim"
metodo_analise = "ssim"

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

# Executa a análise selecionada
img_resultado, tipo_analise, metricas = analisar_diferencas(img_ref, img_teste, metodo = metodo_analise)

# Guardar a imagem de resultado
caminho_resultado = guardar_imagem_resultado(img_resultado, metodo = metodo_analise)

# Separar as métricas adicionais (específicas de cada método de análise)
chaves_basicas = ["num_diferencas", "total_pixels", "pixels_diferentes", "percentagem_diferenca"]
extra_metricas = {k: v for k, v in metricas.items() if k not in chaves_basicas}

# Gerar o relatório PDF
if caminho_resultado:
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
        extra_metricas = extra_metricas
    )
else:
    print("⚠️ A imagem de resultado não foi guardada. O relatório PDF não será gerado.")

# Mostrar a imagem de resultado
cv2.imshow("Diferenças Detetadas", img_resultado)
cv2.waitKey(0)
cv2.destroyAllWindows()