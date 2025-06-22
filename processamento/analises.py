import cv2

# Para análise SSIM
from skimage.metrics import structural_similarity as ssim

def analisar_diferencas(img_ref, img_teste, metodo="absdiff"):
    """
    Executa uma análise de diferenças entre duas imagens com base no método indicado.
    Retorna:
    - imagem com diferenças destacadas
    - descrição do tipo de análise
    - dicionário com métricas
    """
    # Parâmetros visuais comuns
    cor = (0, 0, 255)  # Cor para realce das diferenças (vermelho)
    alpha = 0.7        # Transparência do overlay

    if metodo == "absdiff":
        tipo_analise = "Diferença Absoluta de Pixels (AbsDiff)"

        # Calcular diferença absoluta entre imagens
        diff = cv2.absdiff(img_ref, img_teste)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        # Definir o limiar de diferença (quanto menor, mais sensível à variação de píxels)
        limiar_diferenca = 10

        # Aplicar threshold ao mapa de diferenças para encontrar alterações
        _, mask = cv2.threshold(gray_diff, limiar_diferenca, 255, cv2.THRESH_BINARY)

        # Calcular métricas de diferença
        total_pixels = mask.size
        pixels_diferentes = cv2.countNonZero(mask)
        percentagem_diferenca = (pixels_diferentes / total_pixels) * 100
        print(f"🧮 {pixels_diferentes} pixels diferentes de {total_pixels} ({percentagem_diferenca:.2f}%)")

        # Encontrar contornos nas áreas diferentes
        contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print(f"🔍 {len(contornos)} regiões com diferenças detetadas")

        # Criar imagem de resultado com overlay vermelho nas diferenças
        img_resultado = img_teste.copy()
        overlay = img_resultado.copy()
        for contorno in contornos:
            cv2.drawContours(overlay, [contorno], -1, cor, thickness=cv2.FILLED)
        cv2.addWeighted(overlay, 0.7, img_resultado, 1 - alpha, 0, img_resultado)

        metricas = {
            "num_diferencas": len(contornos),
            "total_pixels": total_pixels,
            "pixels_diferentes": pixels_diferentes,
            "percentagem_diferenca": percentagem_diferenca
        }
        return img_resultado, tipo_analise, metricas

    elif metodo == "histograma":
        tipo_analise = "Comparação de Histograma (Correlação)"

        # Converter imagens para escala de cinzentos
        gray_ref = cv2.cvtColor(img_ref, cv2.COLOR_BGR2GRAY)
        gray_teste = cv2.cvtColor(img_teste, cv2.COLOR_BGR2GRAY)

        # Calcular histogramas
        hist_ref = cv2.calcHist([gray_ref], [0], None, [256], [0, 256])
        hist_teste = cv2.calcHist([gray_teste], [0], None, [256], [0, 256])

        # Normalizar e comparar os histogramas
        hist_ref = cv2.normalize(hist_ref, hist_ref).flatten()
        hist_teste = cv2.normalize(hist_teste, hist_teste).flatten()
        score = cv2.compareHist(hist_ref, hist_teste, cv2.HISTCMP_CORREL)

        # Neste método não há uma imagem com diferenças, por isso devolvemos a imagem original sem diferenças visuais
        img_resultado = img_teste.copy()

        metricas = {
            "correlacao_histogramas": score,
            "num_diferencas": None
        }
        return img_resultado, tipo_analise, metricas

    elif metodo == "ssim":
        tipo_analise = "Índice de Similaridade Estrutural (SSIM)"

        # Converter imagens para escala de cinzentos
        gray_ref = cv2.cvtColor(img_ref, cv2.COLOR_BGR2GRAY)
        gray_teste = cv2.cvtColor(img_teste, cv2.COLOR_BGR2GRAY)

        # Calcular SSIM e mapa de diferenças
        score, diff = ssim(gray_ref, gray_teste, full=True)
        diff = (diff * 255).astype("uint8")

        # Definir o limiar de similaridade (valores mais baixos indicam maiores diferenças)
        # Isolar o que estiver abaixo deste valor
        # O mapa de diferenças SSIM tem valores de 0 (completamente diferente) a 1 (idêntico),
        # mas aqui está escalado para 0–255. Um valor de 220 ≈ 0.86.
        # Com THRESH_BINARY_INV, destacamos píxels com baixa similaridade (abaixo de 220).
        limiar_similaridade = 220

        # Aplicar threshold ao mapa de diferenças para encontrar alterações
        _, mask = cv2.threshold(diff, limiar_similaridade, 255, cv2.THRESH_BINARY_INV)

        # Encontrar contornos nas áreas diferentes
        contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print(f"🔍 {len(contornos)} regiões com diferenças detetadas")

        # Criar imagem de resultado com overlay vermelho nas diferenças
        img_resultado = img_teste.copy()
        overlay = img_resultado.copy()
        for contorno in contornos:
            cv2.drawContours(overlay, [contorno], -1, cor, thickness=cv2.FILLED)
        cv2.addWeighted(overlay, 0.7, img_resultado, 1 - alpha, 0, img_resultado)

        metricas = {
            "indice_ssim": score,
            "num_diferencas": len(contornos)
        }
        return img_resultado, tipo_analise, metricas

    else:
        raise ValueError(f"Método de análise desconhecido: {metodo}")