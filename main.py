import cv2
import os
import time
import uuid

# Importação de funções do módulo de geração de relatórios
from output.relatorio import guardar_imagem_resultado, gerar_relatorio_pdf_multimetodo

# Importação de funções do módulo de análise de diferenças
from processamento.analises import analisar_diferencas

# Lista de métodos de análise a aplicar
metodos_analise = ["absdiff", "histograma", "ssim"]

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

# Inicia contagem do tempo total
inicio_global = time.time()

# Lista para guardar resultados de cada método
resultados = []

# Executa cada método de análise
for metodo in metodos_analise:
    print(f"\n🔎 A executar método: {metodo}")
    inicio = time.time()
    img_resultado, tipo_analise, metricas = analisar_diferencas(img_ref, img_teste, metodo=metodo)
    duracao = time.time() - inicio

    caminho_resultado = None
    if metodo in ["absdiff", "ssim"]:
        caminho_resultado = guardar_imagem_resultado(img_resultado, metodo=metodo, identificador=id_relatorio)

    resultados.append({
        "metodo": metodo,
        "tipo_analise": tipo_analise,
        "metricas": metricas,
        "imagem_resultado": caminho_resultado,
        "duracao": duracao
    })

# Calcula tempo total de execução
duracao_total = time.time() - inicio_global

# Gera o relatório PDF; a imagem de resultado só é obrigatória para métodos com comparação visual (absdiff e ssim)
gerar_relatorio_pdf_multimetodo(
    img_ref_path = IMG_REFERENCIA,
    img_teste_path = IMG_TESTE,
    resultados = resultados,
    identificador = id_relatorio,
    duracao_total = duracao_total
)

# Mostra a imagem de resultado do último método, se existir
if resultados:
    ultima = resultados[-1]
    img_mostrar = None
    if ultima["imagem_resultado"]:
        img_mostrar = cv2.imread(ultima["imagem_resultado"])
    else:
        img_mostrar = img_teste

    if img_mostrar is not None:
        cv2.imshow("Último Resultado de Diferenças Detetadas", img_mostrar)
        cv2.waitKey(0)
        cv2.destroyAllWindows()