import google.generativeai as genai
import tkinter as tk
from tkinter import scrolledtext
from dotenv import load_dotenv
import os
import requests
from PIL import Image, ImageTk
from io import BytesIO

load_dotenv()

# Configura a chave de API para o Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Configurações do modelo Gemini
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Inicializa o modelo com preferência por português
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=(
        "Você é um mestre de RPG."
        "Crie histórias para o jogador, jogue dados para as ações dele e termine a história. "
        "Use NPCs inesperados, monstros e outros elementos de fantasia, respondendo sempre em português."
        "Seja justo e criativo."
        "Sempre peça o nome do jogador antes de começar."
        "Sempre rode uma dado para decidir se a ação do jogador foi bem sucedida ou não."
        "Não se estenda muito, crie poucos parágrafos por vez."
    ),
)

chat_session = model.start_chat(history=[])

# Função para gerar imagens a partir da resposta do Gemini usando a API da Stable Diffusion
def generate_image(prompt):
    url = "https://api.stable diffusion.com/v1/generate"
    headers = {"Content-Type": "application/json"}
    data = {"prompt": prompt, "num_images": 1}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        image_url = response.json()["images"][0]["url"]
        return image_url
    else:
        return None

# Função para enviar a mensagem e obter a resposta e imagem
def send_message():
    player_input = user_input.get()
    if player_input.lower() == "sair":
        window.quit()
    
    # Enviar mensagem para o mestre (API Gemini)
    response = chat_session.send_message(player_input)
    
    # Gerar imagem a partir da resposta do Gemini
    image_url = generate_image(response.text)
    if image_url:
        # Baixar a imagem
        image_response = requests.get(image_url)
        image_data = BytesIO(image_response.content)
        image = Image.open(image_data)
        image.thumbnail((200, 200))  # Redimensionar a imagem
        photo = ImageTk.PhotoImage(image)
        
        # Atualizar a interface com o texto e imagem
        chat_history.insert(tk.END, "Você: " + player_input + "\n")
        chat_history.insert(tk.END, "Mestre: " + response.text + "\n\n")
        imagem_label.config(image=photo)
        imagem_label.image = photo  # Manter a referência à imagem
    else:
        # Mostrar mensagem de erro se a imagem não for gerada
        chat_history.insert(tk.END, "Erro ao gerar imagem.\n")
    
    user_input.delete(0, tk.END)

# Interface gráfica com Tkinter
window = tk.Tk()
window.title("RPG Mestre - Gemini")

# Janela de exibição da conversa
chat_history = scrolledtext.ScrolledText(window, width=50, height=20)
chat_history.pack(pady=10)

# Entrada de texto do jogador
user_input = tk.Entry(window, width=50)
user_input.pack(pady=10)

# Botão de enviar
send_button = tk.Button(window, text="Enviar", command=send_message)
send_button.pack()

# Área para exibir a imagem gerada
imagem_label = tk.Label(window)
imagem_label.pack(pady=10)

# Iniciar a aplicação Tkinter
window.mainloop()