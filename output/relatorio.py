import cv2
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def guardar_imagem_resultado(imagem, prefixo="resultado", metodo = None, identificador = ""):
    """
    Guarda uma imagem no diretório 'relatorios/' com timestamp no nome.
    Retorna o caminho completo do ficheiro guardado ou None em caso de erro.
    """
    pasta = "relatorios"
    os.makedirs(pasta, exist_ok=True)

    # Cria o nome de ficheiro com data e hora
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    sufixo_metodo = f"_{metodo}" if metodo else ""
    nome_ficheiro = f"{prefixo}{sufixo_metodo}_{timestamp}_{identificador}.png"
    caminho = os.path.join(pasta, nome_ficheiro)

    # Guarda a imagem
    sucesso = cv2.imwrite(caminho, imagem)

    if sucesso:
        print(f"✅ Imagem de resultado guardada em: {caminho}")
        return caminho
    else:
        print(f"❌ Falha ao guardar a imagem de resultado em: {caminho}")
        return None

def gerar_observacoes(metodo, metricas):
    """Gera uma observação textual automática com base nas métricas."""
    if metodo == "histograma":
        correlacao = metricas.get("correlacao_histogramas", 0)
        if correlacao > 0.98:
            return "OK As imagens apresentam elevada semelhança de histograma."
        elif correlacao > 0.90:
            return "ATENÇÂO As imagens têm algumas semelhanças no histograma."
        else:
            return "PERIGO As imagens têm histogramas significativamente diferentes."
    elif metodo == "ssim":
        ssim_score = metricas.get("indice_ssim", 0)
        if ssim_score > 0.98:
            return "OK As imagens são estruturalmente quase idênticas."
        elif ssim_score > 0.90:
            return "ATENÇÂO As imagens apresentam alguma semelhança estrutural."
        else:
            return "PERIGO Diferenças estruturais visíveis entre as imagens."
    elif metodo == "absdiff":
        percent = metricas.get("percentagem_diferenca", 0)
        if percent < 2:
            return "OK As imagens são praticamente idênticas."
        elif percent < 10:
            return "ATENÇÃO Diferenças leves detetadas entre as imagens."
        else:
            return "PERIGO Diferenças significativas detetadas entre as imagens."
    return "-"

def gerar_relatorio_pdf_multimetodo(img_ref_path, img_teste_path, resultados, identificador="", duracao_total=None):
    """
    Gera um ficheiro PDF com os dados da comparação e as imagens com legendas.
    """
    pasta = "relatorios"
    os.makedirs(pasta, exist_ok=True)

    # Criar nome do ficheiro PDF com timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_ficheiro = f"relatorio_multimetodo_{timestamp}_{identificador}.pdf"
    caminho = os.path.join(pasta, nome_ficheiro)

    # Iniciar o canvas PDF
    c = canvas.Canvas(caminho, pagesize=A4)
    largura, altura = A4
    margem = 50
    y = altura - margem

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margem, y, "Relatório de Comparação de Imagens (Múltiplos Métodos)")
    y -= 30

    # Info básica
    c.setFont("Helvetica", 11)
    c.drawString(margem, y, f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 20
    c.drawString(margem, y, f"ID do Relatório: {identificador}")
    y -= 20
    if duracao_total is not None:
        c.drawString(margem, y, f"Tempo de Execução: {duracao_total:.2f} segundos")
        y -= 20
    c.drawString(margem, y, f"Imagem de Referência: {img_ref_path}")
    y -= 20
    c.drawString(margem, y, f"Imagem de Teste:      {img_teste_path}")
    y -= 20
    y -= 10

    # Mostrar imagens de referência e teste
    imagens_base = [
        ("Imagem de Referência", img_ref_path),
        ("Imagem de Teste", img_teste_path)
    ]

    for label, path in imagens_base:
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(largura / 2, y, label)
        y -= 20

        imagem_largura = 400
        imagem_altura = 400

        # Confirma se há espaço suficiente antes de desenhar a imagem
        if y < imagem_altura + 50:
            c.showPage()
            y = altura - margem

        # Centra horizontalmente
        try:
            x_centrada = (largura - imagem_largura) / 2
            c.drawImage(path, x_centrada, y - imagem_altura, width=imagem_largura, height=imagem_altura,
                        preserveAspectRatio=True)

        except Exception as e:
            c.setFont("Helvetica", 10)
            c.drawString(margem, y - 20, f"⚠️ Erro ao carregar imagem: {e}")

        y -= imagem_altura + 10

        if y < 200:
            c.showPage()
            y = altura - margem

        # Separador visual
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margem, y, "Resultados por Método de Análise")
    y -= 30

    for resultado in resultados:
        metodo = resultado["metodo"]
        tipo_analise = resultado["tipo_analise"]
        metricas = resultado["metricas"]
        img_resultado_path = resultado["imagem_resultado"]
        duracao = resultado["duracao"]

        c.setFont("Helvetica-Bold", 14)
        c.drawString(margem, y, f"Método: {tipo_analise}")
        y -= 25

        c.setFont("Helvetica", 11)
        num_diferencas = metricas.get("num_diferencas")
        if num_diferencas is not None:
            c.drawString(margem, y, f"Número de diferenças detetadas: {num_diferencas}")
            y -= 20
        else:
            c.drawString(margem, y, "Número de diferenças detetadas: n/a")
            y -= 20

        if "pixels_diferentes" in metricas and "total_pixels" in metricas:
            percentagem = metricas.get("percentagem_diferenca", 0.0)
            c.drawString(margem, y,
                         f"Pixels diferentes: {metricas['pixels_diferentes']} / {metricas['total_pixels']} ({percentagem:.2f}%)")
            y -= 20
        elif metodo in ["histograma", "ssim"]:
            c.drawString(margem, y, "Pixels diferentes: n/a")
            y -= 20

        if metodo == "histograma" and "correlacao_histogramas" in metricas:
            c.drawString(margem, y, f"Correlação dos Histogramas: {metricas['correlacao_histogramas']:.4f} (mais próximo de 1 indica maior semelhança)")
            y -= 20
        elif metodo == "ssim" and "indice_ssim" in metricas:
            c.drawString(margem, y, f"Índice SSIM: {metricas['indice_ssim']:.4f} (mais próximo de 1 indica maior semelhança estrutural)")
            y -= 20
            y -= 10

        # Gerar observação automática
        observacao = gerar_observacoes(metodo, {**metricas, **metricas})
        c.setFont("Helvetica-Oblique", 11)
        c.drawString(margem, y, f"Observação: {observacao}")
        y -= 30

        # Apenas para métodos com resultado visual (absdiff e ssim), incluir imagem de diferenças
        if metodo in ["absdiff", "ssim"] and img_resultado_path:
            c.setFont("Helvetica", 10)
            c.drawString(margem, y, f"Imagem de Resultado: {img_resultado_path}")
            y -= 30

            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(largura / 2, y, "Resultado com Diferenças")
            y -= 20

            # Se não houver espaço suficiente na página, cria uma nova
            if y < 320:
                c.showPage()
                y = altura - margem

            try:
                # Dimensões e centralização horizontal da imagem
                imagem_largura = 400
                imagem_altura = 400
                x_centrada = (largura - imagem_largura) / 2
                c.drawImage(img_resultado_path, x_centrada, y - imagem_altura,
                            width=imagem_largura, height=imagem_altura, preserveAspectRatio=True)
            except Exception as e:
                c.setFont("Helvetica", 10)
                c.drawString(margem, y - 20, f"⚠️ Erro ao carregar imagem: {e}")

            # Ajuste de Y após a imagem
            y -= imagem_altura + 30

            # Confirma se ainda há espaço na página
            if y < 200:
                c.showPage()
                y = altura - margem

        y -= 10

        # Se acabar a página, cria uma nova
        if y < 200:
            c.showPage()
            y = altura - margem

    # Finalizar o PDF
    c.save()
    print(f"📝 PDF gerado com sucesso: {caminho}")