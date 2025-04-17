import cv2
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def guardar_imagem_resultado(imagem, prefixo="resultado"):
    """
    Guarda uma imagem no diretório 'relatorios/' com timestamp no nome.
    Retorna o caminho completo do ficheiro guardado.
    """
    pasta = "relatorios"
    os.makedirs(pasta, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_ficheiro = f"{prefixo}_{timestamp}.png"
    caminho = os.path.join(pasta, nome_ficheiro)

    sucesso = cv2.imwrite(caminho, imagem)

    if sucesso:
        print(f"✅ Imagem de resultado guardada em: {caminho}")
        return caminho
    else:
        print(f"❌ Falha ao guardar a imagem em: {caminho}")
        return None


def gerar_relatorio_pdf(img_ref_path, img_teste_path, img_resultado_path,
                        num_diferencas, total_pixels, pixels_diferentes, percentagem_diferenca):
    """
    Gera um ficheiro PDF com os dados da comparação e as imagens com legendas.
    """
    pasta = "relatorios"
    os.makedirs(pasta, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_ficheiro = f"relatorio_{timestamp}.pdf"
    caminho = os.path.join(pasta, nome_ficheiro)

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
    c.drawString(margem, y, f"Número de diferenças detetadas: {num_diferencas}")
    y -= 20
    c.drawString(margem, y, f"Pixels diferentes: {pixels_diferentes} / {total_pixels} ({percentagem_diferenca:.2f}%)")
    y -= 40

    # Imagens com legendas
    for label, path in [("Imagem de Referência", img_ref_path),
                        ("Imagem de Teste", img_teste_path),
                        ("Resultado com Diferenças", img_resultado_path)]:

        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(largura / 2, y, label)
        y -= 20

        try:
            c.drawImage(path, margem, y - 200, width=200, height=200, preserveAspectRatio=True)
        except Exception as e:
            c.setFont("Helvetica", 10)
            c.drawString(margem, y - 20, f"[Erro ao carregar imagem: {e}]")

        y -= 230

        # Se acabar a página, cria nova
        if y < 200:
            c.showPage()
            y = altura - margem

    c.save()
    print(f"📝 PDF gerado com sucesso: {caminho}")
