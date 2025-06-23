import cv2  # OpenCV para manipulação de imagens (diferenças, histogramas, contornos)

# Para análise SSIM
from skimage.metrics import structural_similarity as ssim

def analisar_diferencas(img_ref, img_teste, metodo="absdiff"):
    """
    Compara duas imagens utilizando o método escolhido e retorna análise detalhada.

    Esta função é o núcleo do sistema de comparação, com três métodos Disponíveis:
    - "absdiff": Diferença absoluta pixel-a-pixel, ideal para detetar alterações pontuais
    - "histograma": Compara distribuição de intensidades, útil para mudanças globais de cor/brilho
    - "ssim": Índice de Similaridade Estrutural, com foco em mudanças na estrutura da imagem

    Parâmetros:
        img_ref: Imagem de referência
        img_teste: Imagem de teste a comparar
        metodo: Método de análise a aplicar (string)

    Retorna:
        tuple: (imagem_resultado, tipo_analise, metricas)
            - imagem_resultado: Imagem com diferenças destacadas visualmente
            - tipo_analise: Descrição em texto do método usado
            - metricas: Dicionário com valores quantitativos da análise
    """

    # Parâmetros para destacar diferenças visualmente em todos os métodos
    cor = (0, 0, 255)  # Cor para realce das diferenças (vermelho)
    alpha = 0.7        # Transparência do overlay (0.0=transparente, 1.0=opaco)

    # Método 1: diferença absoluta de pixels (absdiff)
    if metodo == "absdiff":
        tipo_analise = "Diferença Absoluta de Pixels (AbsDiff)"

        # Calcula a diferença absoluta entre as duas imagens pixel a pixel
        # Resultado: imagem onde cada pixel = |pixel_ref - pixel_teste|
        diff = cv2.absdiff(img_ref, img_teste)

        # Converte para escala de cinzentos para facilitar a análise de threshold
        # Necessário porque trabalhamos com uma única intensidade por pixel
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        # Define o limiar de sensibilidade para considerar uma diferença significativa
        # Valores baixos (ex: 5) = mais sensível, deteta variações pequenas
        # Valores altos (ex: 30) = menos sensível, só deteta alterações óbvias
        limiar_diferenca = 10

        # Aplica threshold binário para criar máscara de diferenças
        # Pixels com diferença > limiar_diferenca ficam brancos (255)
        # Pixels com diferença <= limiar_diferenca ficam pretos (0)
        _, mask = cv2.threshold(gray_diff, limiar_diferenca, 255, cv2.THRESH_BINARY)

        # Conta o número total de pixels na imagem (largura × altura)
        total_pixels = mask.size

        # Conta pixels brancos na máscara (pixels diferentes)
        pixels_diferentes = cv2.countNonZero(mask)

        # Calcula percentagem de pixels que são diferentes
        percentagem_diferenca = (pixels_diferentes / total_pixels) * 100
        print(f"🧮 {pixels_diferentes} pixels diferentes de {total_pixels} ({percentagem_diferenca:.2f}%)")

        # Encontra contornos das regiões diferentes com a máscara binária
        # RETR_EXTERNAL: só contornos externos (não contornos dentro de outros)
        # CHAIN_APPROX_SIMPLE: comprime contornos e remove pontos redundantes
        contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print(f"🔍 {len(contornos)} regiões com diferenças detetadas")

        # Cria cópia da imagem de teste para desenhar as diferenças
        img_resultado = img_teste.copy()
        overlay = img_resultado.copy()

        # Desenha cada contorno preenchido na cor vermelha
        for contorno in contornos:
            cv2.drawContours(overlay, [contorno], -1, cor, thickness=cv2.FILLED)

        # Combina overlay com imagem original e utilizando transparência
        # Fórmula: resultado = (overlay * alpha) + (original * (1-alpha))
        cv2.addWeighted(overlay, 0.7, img_resultado, 1 - alpha, 0, img_resultado)

        # Métricas a retornar
        metricas = {
            "num_diferencas": len(contornos),                   # Número de regiões diferentes
            "total_pixels": total_pixels,                       # Total de pixels na imagem
            "pixels_diferentes": pixels_diferentes,             # Pixels que diferem
            "percentagem_diferenca": percentagem_diferenca      # % de diferença
        }
        return img_resultado, tipo_analise, metricas

    # Método 2: comparação de histograma (correlação)
    elif metodo == "histograma":
        tipo_analise = "Comparação de Histograma (Correlação)"

        # Converte ambas as imagens para a escala de cinzentos
        # Histograma analisa distribuição de intensidades, não precisa de cor
        gray_ref = cv2.cvtColor(img_ref, cv2.COLOR_BGR2GRAY)
        gray_teste = cv2.cvtColor(img_teste, cv2.COLOR_BGR2GRAY)

        # Calcula histograma da imagem de referência
        hist_ref = cv2.calcHist([gray_ref], [0], None, [256], [0, 256])
        hist_teste = cv2.calcHist([gray_teste], [0], None, [256], [0, 256])

        # Normaliza histogramas para comparação
        # Remove influência do tamanho total da imagem
        hist_ref = cv2.normalize(hist_ref, hist_ref).flatten()
        hist_teste = cv2.normalize(hist_teste, hist_teste).flatten()

        # Calcula correlação entre histogramas usando método de correlação
        # HISTCMP_CORREL: retorna valor entre -1 e 1
        # 1 = correlação perfeita (histogramas idênticos)
        # 0 = sem correlação
        # -1 = correlação negativa perfeita
        score = cv2.compareHist(hist_ref, hist_teste, cv2.HISTCMP_CORREL)

        # O método de histograma não gera imagem de diferenças visuais
        # Retorna imagem original pois a análise é estatística, não espacial
        img_resultado = img_teste.copy()

        # Métricas específicas do método histograma
        metricas = {
            "correlacao_histogramas": score,
            "num_diferencas": None
        }
        return img_resultado, tipo_analise, metricas

    # Método 3: índice de similaridade estrutural (SSIM)
    elif metodo == "ssim":
        tipo_analise = "Índice de Similaridade Estrutural (SSIM)"

        # Converte imagens para escala de cinzentos
        gray_ref = cv2.cvtColor(img_ref, cv2.COLOR_BGR2GRAY)
        gray_teste = cv2.cvtColor(img_teste, cv2.COLOR_BGR2GRAY)

        # Calcula SSIM com mapa completo de diferenças
        # score: valor global de similaridade (0 a 1, onde 1 = idêntico)
        # diff: mapa pixel-a-pixel de similaridade estrutural
        # full=True: retorna tanto o score global quanto o mapa detalhado
        score, diff = ssim(gray_ref, gray_teste, full=True)
        diff = (diff * 255).astype("uint8")

        # Define limiar de similaridade estrutural
        # Valores mais baixos no mapa SSIM indicam maiores diferenças estruturais
        # 220/255 ≈ 0.86 de similaridade mínima aceitável
        limiar_similaridade = 220

        # Aplica threshold invertido (THRESH_BINARY_INV) ao mapa de diferenças para encontrar alterações
        # Pixels com similaridade < limiar_similaridade ficam brancos (diferentes)
        # Pixels com similaridade >= limiar_similaridade ficam pretos (similares)
        _, mask = cv2.threshold(diff, limiar_similaridade, 255, cv2.THRESH_BINARY_INV)

        # Encontra contornos das regiões com baixa similaridade estrutural
        contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print(f"🔍 {len(contornos)} regiões com diferenças detetadas")

        # Cria visualização com overlay vermelho nas diferenças estruturais
        img_resultado = img_teste.copy()
        overlay = img_resultado.copy()

        # Desenha contornos preenchidos para destacar diferenças estruturais
        for contorno in contornos:
            cv2.drawContours(overlay, [contorno], -1, cor, thickness=cv2.FILLED)

        # Aplica overlay com transparência
        cv2.addWeighted(overlay, 0.7, img_resultado, 1 - alpha, 0, img_resultado)

        # Métricas específicas de SSIM
        metricas = {
            "indice_ssim": score,               # Índice global de similaridade estrutural
            "num_diferencas": len(contornos)    # Número de regiões com diferenças estruturais
        }
        return img_resultado, tipo_analise, metricas

    else:
        # Exceção se método especificado não for válido
        # Ajuda a detetar erros nos nomes dos métodos
        raise ValueError(f"Método de análise desconhecido: {metodo}")