import cv2
import numpy as np
import os

# Criar diretórios de destino, se não existirem
os.makedirs("imagens/referencia", exist_ok = True)
os.makedirs("imagens/teste", exist_ok = True)

# Tamanho da imagem que vai ser criada
altura, largura = 300, 300

# Criar imagem de referência (branco + quadrado azul)
img_referencia = np.ones((altura, largura, 3), dtype = np.uint8) * 255
cv2.rectangle(img_referencia, (100, 100), (200, 200), (255, 0, 0), -1)  # Quadrado azul

# Criar imagem de teste (igual, mas com um círculo verde)
img_teste = img_referencia.copy()
cv2.circle(img_teste, (150, 150), 20, (0, 255, 0), -1)  # Círculo verde

# Guardar imagens nos respetivos diretórios
cv2.imwrite("imagens/referencia/exemplo.png", img_referencia)
cv2.imwrite("imagens/teste/exemplo.png", img_teste)

print("✅ Imagens de teste geradas com sucesso!")