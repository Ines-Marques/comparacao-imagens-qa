import cv2  # OpenCV para manipulação de imagens
import os   # Operações com sistema de ficheiros
import time # Medição de tempo de execução
import uuid # Geração de identificadores únicos para identificação de sessões

# Importação de funções do módulo de geração de relatórios
from output.relatorio import guardar_imagem_resultado, gerar_relatorio_pdf_multimetodo

# Importação de funções do módulo de análise de diferenças
from processamento.analises import analisar_diferencas

# Lista de métodos de análise a aplicar sequencialmente
metodos_analise = ["absdiff", "histograma", "ssim"]

# Definir caminhos das imagens de referência e de teste
# IMG_NOME: Nome do ficheiro de imagem a analisar (deve existir em ambas as pastas)
IMG_NOME = "menu.png"

# Constrói caminhos completos para as imagens usando os.path.join()
# Garante compatibilidade entre sistemas operativos
IMG_REFERENCIA = os.path.join("imagens", "referencia", IMG_NOME)
IMG_TESTE = os.path.join("imagens", "teste", IMG_NOME)

# Carregar imagens pelo OpenCV
# cv2.imread() retorna array com dados da imagem ou None se falhar
img_ref = cv2.imread(IMG_REFERENCIA)
img_teste = cv2.imread(IMG_TESTE)

# Verifica se ambas as imagens foram carregadas corretamente
# Falha pode ocorrer por: ficheiro inexistente, formato inválido
if img_ref is None:
    print(f"❌ Imagem de referência não encontrada: {IMG_REFERENCIA}")
    exit(1)

if img_teste is None:
    print(f"❌ Imagem de teste não encontrada: {IMG_TESTE}")
    exit(1)

# Verifica se as imagens têm o mesmo tamanho (altura, largura)
# Comparação direta só é possível com dimensões idênticas
if img_ref.shape != img_teste.shape:
    print("❌ As imagens têm tamanhos diferentes e não podem ser comparadas diretamente.")
    exit(1)

# Gera identificador único para esta sessão de análise
id_relatorio = str(uuid.uuid4())[:8]

# Inicia contagem do tempo total de execução
# Permite medir performance geral do sistema de análise
inicio_global = time.time()

# Lista para guardar resultados de cada método aplicado
# Cada elemento será um dicionário com:
# - metodo: nome do método usado
# - tipo_analise: descrição textual do método
# - metricas: valores quantitativos calculados
# - imagem_resultado: caminho da imagem com diferenças destacadas
# - duracao: tempo de execução específico deste método
resultados = []

# Executa cada método de análise sequencialmente
for metodo in metodos_analise:
    print(f"\n🔎 A executar método: {metodo}")

    # Marca início da execução deste método específico
    # Permite medir performance individual de cada algoritmo
    inicio = time.time()

    # Retorna a imagem com diferenças destacadas, descrição do tipo, métricas calculadas
    img_resultado, tipo_analise, metricas = analisar_diferencas(img_ref, img_teste, metodo=metodo)

    # Calcula tempo decorrido para este método
    duracao = time.time() - inicio

    # Inicializa caminho do resultado como None
    # Só alguns métodos geram imagens de resultado visual
    caminho_resultado = None

    # Guarda imagem de resultado apenas para métodos que geram visualizações
    # "absdiff" e "ssim" criam imagens com diferenças destacadas visualmente
    # "histograma" é análise estatística sem componente visual
    if metodo in ["absdiff", "ssim"]:
        caminho_resultado = guardar_imagem_resultado(img_resultado, metodo=metodo, identificador=id_relatorio)

    # Adiciona resultado deste método à lista de resultados
    resultados.append({
        "metodo": metodo,                           # Nome do método aplicado
        "tipo_analise": tipo_analise,               # Descrição textual do método
        "metricas": metricas,                       # Dicionário com valores calculados
        "imagem_resultado": caminho_resultado,      # Caminho da imagem
        "duracao": duracao                          # Tempo de execução em segundos
    })

# Calcula tempo total de execução de todos os métodos
duracao_total = time.time() - inicio_global

# Gera o relatório PDF com todos os resultados
# Parâmetros:
# - img_ref_path: caminho da imagem de referência
# - img_teste_path: caminho da imagem de teste
# - resultados: lista completa com resultados de todos os métodos
# - identificador: ID único desta sessão
# - duracao_total: tempo total de execução
gerar_relatorio_pdf_multimetodo(
    img_ref_path = IMG_REFERENCIA,
    img_teste_path = IMG_TESTE,
    resultados = resultados,
    identificador = id_relatorio,
    duracao_total = duracao_total
)