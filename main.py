import cv2
import numpy as np
import os

from output.relatorio import guardar_imagem_resultado, gerar_relatorio_pdf

# Caminhos das imagens
IMG_NOME = "exemplo.png"
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

# Garante que têm o mesmo tamanho
if img_ref.shape != img_teste.shape:
    print("❌ As imagens têm tamanhos diferentes e não podem ser comparadas diretamente.")
    exit(1)

# Calcula a diferença absoluta entre as imagens
diff = cv2.absdiff(img_ref, img_teste)

# Converte para escala de cinzentos para facilitar visualização
gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

# Aplica um threshold para realçar apenas diferenças visíveis
_, mask = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)

# Total de pixels
total_pixels = mask.size

# Pixels diferentes (mask > 0)
pixels_diferentes = cv2.countNonZero(mask)

# Percentagem de diferença
percentagem_diferenca = (pixels_diferentes / total_pixels) * 100
print(f"🧮 {pixels_diferentes} pixels diferentes de {total_pixels} ({percentagem_diferenca:.2f}%)")

# Encontrar contornos das áreas diferentes
contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print(f"🔍 {len(contornos)} regiões com diferenças detetadas")

# Criar imagem de resultado com overlay transparente
img_resultado = img_teste.copy()
overlay = img_resultado.copy()

# Cor do destaque: vermelho
cor = (0, 0, 255)

# Preencher as áreas diferentes na máscara
for contorno in contornos:
    cv2.drawContours(overlay, [contorno], -1, cor, thickness=cv2.FILLED)

# Combinar a imagem com o overlay usando transparência
alpha = 0.7  # transparência
cv2.addWeighted(overlay, alpha, img_resultado, 1 - alpha, 0, img_resultado)

# Guardar a imagem de resultado e obter o caminho
caminho_resultado = guardar_imagem_resultado(img_resultado)

# Gerar o relatório PDF
if caminho_resultado:
    gerar_relatorio_pdf(
        img_ref_path=IMG_REFERENCIA,
        img_teste_path=IMG_TESTE,
        img_resultado_path=caminho_resultado,
        num_diferencas=len(contornos),
        total_pixels=total_pixels,
        pixels_diferentes=pixels_diferentes,
        percentagem_diferenca=percentagem_diferenca
    )
else:
    print("⚠️ Imagem de resultado não foi guardada. Relatório PDF não será gerado.")

# Mostrar a imagem resultante
cv2.imshow("Diferenças Detetadas", img_resultado)
cv2.waitKey(0)
cv2.destroyAllWindows()
