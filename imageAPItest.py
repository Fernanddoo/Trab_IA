import google.generativeai as genai
import tkinter as tk
from tkinter import scrolledtext
from dotenv import load_dotenv
import os
import requests
from PIL import Image, ImageTk
from io import BytesIO

# Carregar variáveis de ambiente
load_dotenv()

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Configurações do modelo Gemini
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=(
        "Você é um mestre de RPG."
        "Crie histórias para o jogador, jogue dados para as ações dele e termine a história. "
        "Use NPCs inesperados, monstros e outros elementos de fantasia, respondendo sempre em português."
        "Seja justo e criativo."
        "Sempre peça o nome do jogador antes de começar."
        "Sempre rode um dado para decidir se a ação do jogador foi bem sucedida ou não."
        "Não se estenda muito, crie poucos parágrafos por vez."
    ),
)

chat_session = model.start_chat(history=[])

# Função para gerar imagens a partir da resposta do Gemini usando a API da Hugging Face
def generate_image(prompt):
    api_key = os.getenv("HF_API_KEY")
    API_URL = "https://api-inference.huggingface.co/models/ZB-Tech/Text-to-Image"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    data = {"inputs": prompt}
    
    response = requests.post(API_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.content
    else:
        return None

# Função para enviar a mensagem e obter a resposta e imagem
def send_message():
    player_input = user_input.get()
    if player_input.lower() == "sair":
        window.quit()

    response = chat_session.send_message(player_input)

    image_data = generate_image(response.text)
    
    if image_data:
        # Processar e exibir a imagem
        image = Image.open(BytesIO(image_data))
        image.thumbnail((400, 400)) 
        photo = ImageTk.PhotoImage(image)

        # Atualizar a interface com o texto e a imagem
        chat_history.insert(tk.END, "Você: " + player_input + "\n")
        chat_history.insert(tk.END, "Mestre: " + response.text + "\n\n")
        imagem_label.config(image=photo)
        imagem_label.image = photo  
    else:
        # Mostrar mensagem de erro se a imagem não for gerada
        chat_history.insert(tk.END, "Erro ao gerar imagem.\n")
    
    user_input.delete(0, tk.END)

# Interface gráfica com Tkinter
window = tk.Tk()
window.title("RPG Mestre - Gemini")

frame = tk.Frame(window)
frame.pack(pady=20, padx=20)

chat_history = scrolledtext.ScrolledText(frame, width=100, height=50)
chat_history.grid(row=0, column=0, columnspan=2)

user_input = tk.Entry(frame, width=70)
user_input.grid(row=1, column=0, pady=10)

send_button = tk.Button(frame, text="Enviar", command=send_message)
send_button.grid(row=1, column=1, pady=15)

imagem_label = tk.Label(frame)
imagem_label.grid(row=1, column=2, padx=10)

# Iniciar a aplicação Tkinter
window.mainloop()
