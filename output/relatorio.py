import cv2
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def guardar_imagem_resultado(imagem, prefixo="resultado", metodo = None):
    """
    Guarda uma imagem no diretório 'relatorios/' com timestamp no nome.
    Retorna o caminho completo do ficheiro guardado ou None em caso de erro.
    """
    pasta = "relatorios"
    os.makedirs(pasta, exist_ok=True)

    # Cria o nome de ficheiro com data e hora
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    sufixo_metodo = f"_{metodo}" if metodo else ""
    nome_ficheiro = f"{prefixo}{sufixo_metodo}_{timestamp}.png"
    caminho = os.path.join(pasta, nome_ficheiro)

    # Guarda a imagem
    sucesso = cv2.imwrite(caminho, imagem)

    if sucesso:
        print(f"✅ Imagem de resultado guardada em: {caminho}")
        return caminho
    else:
        print(f"❌ Falha ao guardar a imagem de resultado em: {caminho}")
        return None


def gerar_relatorio_pdf(img_ref_path, img_teste_path, img_resultado_path,
                        num_diferencas, total_pixels, pixels_diferentes, percentagem_diferenca, tipo_analise, metodo = None, extra_metricas = None):
    """
    Gera um ficheiro PDF com os dados da comparação e as imagens com legendas.
    """
    pasta = "relatorios"
    os.makedirs(pasta, exist_ok=True)

    # Criar nome do ficheiro PDF com timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    sufixo_metodo = f"_{metodo}" if metodo else ""
    nome_ficheiro = f"relatorio{sufixo_metodo}_{timestamp}.pdf"
    caminho = os.path.join(pasta, nome_ficheiro)

    # Iniciar o canvas PDF
    c = canvas.Canvas(caminho, pagesize=A4)
    largura, altura = A4
    margem = 50
    y = altura - margem

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margem, y, "Relatório de Comparação de Imagens")
    y -= 30

    # Info básica
    c.setFont("Helvetica", 11)
    c.drawString(margem, y, f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 20
    c.drawString(margem, y, f"Imagem de Referência: {img_ref_path}")
    y -= 20
    c.drawString(margem, y, f"Imagem de Teste:      {img_teste_path}")
    y -= 20
    c.drawString(margem, y, f"Imagem de Resultado:  {img_resultado_path}")
    y -= 20
    c.drawString(margem, y, f"Tipo de Análise: {tipo_analise}")
    y -= 20

    if num_diferencas is not None:
        c.drawString(margem, y, f"Número de diferenças detetadas: {num_diferencas}")
        y -= 20
    elif metodo in ["histograma", "ssim"]:
        c.drawString(margem, y, "Número de diferenças detetadas: n/a")
        y -= 20

    if pixels_diferentes is not None and total_pixels is not None:
        c.drawString(margem, y,
                     f"Pixels diferentes: {pixels_diferentes} / {total_pixels} ({percentagem_diferenca:.2f}%)")
        y -= 20
    elif metodo in ["histograma", "ssim"]:
        c.drawString(margem, y, "Pixels diferentes: n/a")
        y -= 20

    if metodo == "histograma" and "correlacao_histogramas" in extra_metricas:
        c.drawString(margem, y,
                     f"Correlação dos Histogramas: {extra_metricas['correlacao_histogramas']} (mais próximo de 1 indica maior semelhança)")
        y -= 20
    elif metodo == "ssim" and "indice_ssim" in extra_metricas:
        c.drawString(margem, y,
                     f"Índice SSIM: {extra_metricas['indice_ssim']} (mais próximo de 1 indica maior semelhança estrutural)")
        y -= 20
    y -= 20

    # Lista inicial com as duas imagens base (referência e teste)
    imagens_para_inserir = [
        ("Imagem de Referência", img_ref_path),
        ("Imagem de Teste", img_teste_path)
    ]

    # Apenas para métodos com resultado visual (absdiff e ssim), incluir imagem de diferenças
    if metodo in ["absdiff", "ssim"]:
        imagens_para_inserir.append(("Resultado com Diferenças", img_resultado_path))

    # Adiciona as imagens ao relatório
    for label, path in imagens_para_inserir:
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(largura / 2, y, label)
        y -= 20

        try:
            # Inserir a imagem
            c.drawImage(path, margem, y - 200, width=200, height=200, preserveAspectRatio=True)
        except Exception as e:
            # Caso a imagem falhe, escrever aviso
            c.setFont("Helvetica", 10)
            c.drawString(margem, y - 20, f"⚠️ Erro ao carregar imagem: {e}")

        y -= 230

        # Se acabar a página, cria uma nova
        if y < 200:
            c.showPage()
            y = altura - margem

    # Finalizar o PDF
    c.save()
    print(f"📝 PDF gerado com sucesso: {caminho}")