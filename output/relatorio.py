import cv2 # OpenCV para manipulação de imagens
import os # Operações com sistema de ficheiros
from datetime import datetime # Para geração de timestamps únicos nos nomes de ficheiros
from reportlab.lib.pagesizes import A4 # Define o tamanho padrão da página PDF
from reportlab.pdfgen import canvas # Biblioteca principal para geração de PDFs

def guardar_imagem_resultado(imagem, prefixo="resultado", metodo = None, identificador = ""):
    """
    Guarda uma imagem processada no diretório 'relatorios/' com nome único baseado no timestamp.

    Parâmetros:
        imagem: Array numpy da imagem OpenCV a guardar
        prefixo: Prefixo do nome do ficheiro ("resultado")
        metodo: Nome do método usado na análise (para incluir no nome)
        identificador: ID único da sessão de análise

    Retorna:
        str: Caminho completo do ficheiro guardado
        None: Em caso de erro ao guardar
    """

    # Define e cria o diretório de output se não existir
    pasta = "relatorios"
    os.makedirs(pasta, exist_ok=True)

    # Cria o nome de ficheiro com o timestamp atual
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Adiciona sufixo do método se fornecido (ex: "_absdiff", "_ssim")
    sufixo_metodo = f"_{metodo}" if metodo else ""

    # Nome final: resultado_absdiff_2024-06-23_14-30-45_abc123.png
    nome_ficheiro = f"{prefixo}{sufixo_metodo}_{timestamp}_{identificador}.png"
    caminho = os.path.join(pasta, nome_ficheiro)

    # Tenta guardar a imagem
    sucesso = cv2.imwrite(caminho, imagem)

    # Feedback sobre o resultado da operação
    if sucesso:
        print(f"✅ Imagem de resultado guardada em: {caminho}")
        return caminho
    else:
        print(f"❌ Falha ao guardar a imagem de resultado em: {caminho}")
        return None

def gerar_observacoes(metodo, metricas):
    """
        Gera observações textuais automáticas baseadas nos resultados da análise.
        Interpreta as métricas numéricas e converte em avaliações qualitativas.

        Parâmetros:
            metodo: Nome do método usado ("histograma", "ssim", "absdiff")
            metricas: Dicionário com valores calculados pelo método

        Retorna:
            str: Observação textual classificada (OK/ATENÇÃO/PERIGO)
        """

    # Análise baseada em correlação de histogramas (distribuição de cores)
    if metodo == "histograma":
        correlacao = metricas.get("correlacao_histogramas", 0)

        # Thresholds para classificação da semelhança
        if correlacao > 0.98:       # Correlação muito alta
            return "OK As imagens apresentam elevada semelhança de histograma."
        elif correlacao > 0.90:     # Correlação moderada
            return "ATENÇÃO As imagens têm algumas semelhanças no histograma."
        else:                       # Correlação baixa
            return "PERIGO As imagens têm histogramas significativamente diferentes."

    # Análise baseada em SSIM (Structural Similarity Index)
    elif metodo == "ssim":
        ssim_score = metricas.get("indice_ssim", 0)

        # Thresholds para similaridade estrutural
        if ssim_score > 0.98:       # SSIM muito alto (estrutura quase idêntica)
            return "OK As imagens são estruturalmente quase idênticas."
        elif ssim_score > 0.90:     # SSIM moderado (alguma semelhança estrutural)
            return "ATENÇÂO As imagens apresentam alguma semelhança estrutural."
        else:                       # SSIM baixo (diferenças estruturais significativas)
            return "PERIGO Diferenças estruturais visíveis entre as imagens."

    # Análise baseada em diferença absoluta (pixel a pixel)
    elif metodo == "absdiff":
        percent = metricas.get("percentagem_diferenca", 0)

        # Thresholds para percentagem de pixels diferentes
        if percent < 2:             # Menos de 2% de diferença
            return "OK As imagens são praticamente idênticas."
        elif percent < 10:          # 2-10% de diferença
            return "ATENÇÃO Diferenças leves detetadas entre as imagens."
        else:                       # Mais de 10% de diferença
            return "PERIGO Diferenças significativas detetadas entre as imagens."

    # Método não reconhecido ou sem métricas
    return "-"

def gerar_relatorio_pdf_multimetodo(img_ref_path, img_teste_path, resultados, identificador = "", duracao_total = None):
    """
    Gera um relatório PDF completo com análise de múltiplos métodos.

    O relatório incluí:
    - Informações gerais (data, tempo, ID, caminhos das imagens)
    - Visualização das imagens de referência e teste
    - Resultados detalhados de cada método aplicado
    - Imagens de diferenças (quando aplicável)
    - Observações automáticas para cada método

    Parâmetros:
        img_ref_path: Caminho para a imagem de referência
        img_teste_path: Caminho para a imagem de teste
        resultados: Lista de dicionários com resultados de cada método
        identificador: ID único desta sessão de análise
        duracao_total: Tempo total de execução
    """

    # Preparação do ficheiro de output
    pasta = "relatorios"
    os.makedirs(pasta, exist_ok = True)

    # Criar nome único do ficheiro PDF com timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_ficheiro = f"relatorio_multimetodo_{timestamp}_{identificador}.pdf"
    caminho = os.path.join(pasta, nome_ficheiro)

    # Cria o canvas PDF com tamanho A4
    c = canvas.Canvas(caminho, pagesize = A4)
    largura, altura = A4
    margem = 50         # Margem de 50 pontos em todas as bordas
    y = altura - margem # Posição Y inicial (começa do topo)

    # Título principal do relatório
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margem, y, "Relatório de Comparação de Imagens (Múltiplos Métodos)")
    y -= 30

    # Informações básicas da sessão
    c.setFont("Helvetica", 11)
    c.drawString(margem, y, f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 20
    c.drawString(margem, y, f"ID do Relatório: {identificador}")
    y -= 20

    # Tempo de execução
    if duracao_total is not None:
        c.drawString(margem, y, f"Tempo de Execução: {duracao_total:.2f} segundos")
        y -= 20

    # Caminhos das imagens analisadas
    c.drawString(margem, y, f"Imagem de Referência: {img_ref_path}")
    y -= 20
    c.drawString(margem, y, f"Imagem de Teste:      {img_teste_path}")
    y -= 20
    y -= 10

    # Lista com as imagens base a incluir no relatório
    imagens_base = [
        ("Imagem de Referência", img_ref_path),
        ("Imagem de Teste", img_teste_path)
    ]

    # Processa cada imagem base
    for label, path in imagens_base:
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(largura / 2, y, label)  # Centra o título
        y -= 20

        # Dimensões das imagens no PDF
        imagem_largura = 400
        imagem_altura = 400

        # Confirma se há espaço suficiente na página atual antes de desenhar a imagem
        if y < imagem_altura + 50:
            c.showPage()            # Cria nova página
            y = altura - margem     # Reset da posição Y

        # Tenta inserir a imagem no PDF
        try:
            x_centrada = (largura - imagem_largura) / 2      # Centra horizontalmente a imagem no PDF
            c.drawImage(path, x_centrada, y - imagem_altura, width = imagem_largura, height = imagem_altura,
                        preserveAspectRatio = True)            # Mantém proporções originais

        # Em caso de erro (ficheiro não encontrado, formato inválido, etc.)
        except Exception as e:
            c.setFont("Helvetica", 10)
            c.drawString(margem, y - 20, f"⚠️ Erro ao carregar imagem: {e}")

        # Ajusta posição Y após a imagem
        y -= imagem_altura + 10

        # Verifica se é necessário quebra de página
        if y < 200:
            c.showPage()
            y = altura - margem

    # Título da secção de resultados
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margem, y, "Resultados por Método de Análise")
    y -= 30

    # Processa cada resultado de método
    for resultado in resultados:
        # Extrai dados do resultado atual
        metodo = resultado["metodo"]                            # Nome do método ("absdiff", "ssim", "histograma")
        tipo_analise = resultado["tipo_analise"]                # Descrição do tipo de análise
        metricas = resultado["metricas"]                        # Dicionário com valores calculados
        img_resultado_path = resultado["imagem_resultado"]      # Caminho da imagem de resultado
        duracao = resultado["duracao"]                          # Tempo de execução deste método

        # Título do método atual
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margem, y, f"Método: {tipo_analise}")
        y -= 25

        c.setFont("Helvetica", 11)

        # Tempo de execução do método
        c.drawString(margem, y, f"Tempo de execução: {duracao:.2f} segundos")
        y -= 20

        # Número de diferenças detetadas
        num_diferencas = metricas.get("num_diferencas")
        if num_diferencas is not None:
            c.drawString(margem, y, f"Número de diferenças detetadas: {num_diferencas}")
            y -= 20
        else:
            c.drawString(margem, y, "Número de diferenças detetadas: n/a")
            y -= 20

        # Percentagem de pixels diferentes (para método pixel-a-pixel)
        if "pixels_diferentes" in metricas and "total_pixels" in metricas:
            percentagem = metricas.get("percentagem_diferenca", 0.0)
            c.drawString(margem, y,
                         f"Pixels diferentes: {metricas['pixels_diferentes']} / {metricas['total_pixels']} ({percentagem:.2f}%)")
            y -= 20
        elif metodo in ["histograma", "ssim"]:
            # Métodos que não fazem comparação pixel-a-pixel
            c.drawString(margem, y, "Pixels diferentes: n/a")
            y -= 20

        # Métricas específicas por método
        if metodo == "histograma" and "correlacao_histogramas" in metricas:
            # Correlação de histogramas (0 a 1, onde 1 = idêntico)
            c.drawString(margem, y, f"Correlação dos Histogramas: {metricas['correlacao_histogramas']:.4f} (mais próximo de 1 indica maior semelhança)")
            y -= 20
        elif metodo == "ssim" and "indice_ssim" in metricas:
            # Índice SSIM (0 a 1, onde 1 = estruturalmente idêntico)
            c.drawString(margem, y, f"Índice SSIM: {metricas['indice_ssim']:.4f} (mais próximo de 1 indica maior semelhança estrutural)")
            y -= 20
            y -= 10

        # Gera observação qualitativa baseada nas métricas
        observacao = gerar_observacoes(metodo, metricas)
        c.setFont("Helvetica-Oblique", 11)      # Itálico para destacar observações
        c.drawString(margem, y, f"Observação: {observacao}")
        y -= 30

        # Só inclui imagem para métodos que geram visualizações de diferenças
        if metodo in ["absdiff", "ssim"] and img_resultado_path:
            # Indica o caminho da imagem de resultado
            c.setFont("Helvetica", 10)
            c.drawString(margem, y, f"Imagem de Resultado: {img_resultado_path}")
            y -= 30

            # Título da imagem de resultado
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(largura / 2, y, "Resultado com Diferenças")
            y -= 20

            # Se não houver espaço suficiente na página, cria uma nova
            if y < 320:
                c.showPage()
                y = altura - margem

            # Tenta inserir a imagem de resultado
            try:
                # Dimensões e centralização horizontal da imagem
                imagem_largura = 400
                imagem_altura = 400
                x_centrada = (largura - imagem_largura) / 2
                c.drawImage(img_resultado_path, x_centrada, y - imagem_altura,
                            width = imagem_largura, height = imagem_altura, preserveAspectRatio = True)
            except Exception as e:
                # Erro a carregar imagem de resultado
                c.setFont("Helvetica", 10)
                c.drawString(margem, y - 20, f"⚠️ Erro ao carregar imagem: {e}")

            # Ajuste da posição Y após a imagem
            y -= imagem_altura + 30

            # Confirma se ainda há espaço na página
            if y < 200:
                c.showPage()
                y = altura - margem

        y -= 10     # Espaço entre métodos

        # Se acabar a página, cria uma nova
        if y < 200:
            c.showPage()
            y = altura - margem

    # Guarda e fecha o ficheiro PDF
    c.save()
    print(f"📝 PDF gerado com sucesso: {caminho}")