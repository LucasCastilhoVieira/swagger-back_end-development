import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import requests
import json
import threading
open_ia_key = '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'

class APISwaggerDevelopment:
    def __init__(self, root):
        self.root = root
        self.root.title("Swagger de API-test")
        self.routes = []

    
        self.root.configure(bg="#121212")
        self.root.state("zoomed")  
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg="#121212")
        main_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(main_frame, bg="#121212", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)

        self.routes_container = tk.Frame(canvas, bg="#121212")

        self.routes_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

  
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", _on_mousewheel)    
        canvas.bind_all("<Button-5>", _on_mousewheel)

        self.window_item = canvas.create_window((0, 0), window=self.routes_container, anchor="n")

        def on_canvas_configure(event):
 
            canvas.itemconfig(self.window_item, width=event.width)

            canvas.coords(self.window_item, event.width/2, 0)
        canvas.bind("<Configure>", on_canvas_configure)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
       
        base_frame = tk.Frame(self.routes_container, pady=10, bg="#121212")
        base_frame.pack(fill="x", padx=20)
        tk.Label(base_frame, text="🔗 Base da API:", font=("Source Code Pro", 20, "bold"), bg="#121212", fg="white").pack(anchor="w")
        self.base_url_entry = tk.Entry(base_frame, font=("Source Code Pro", 20), bg="#1e1e1e", fg="white", insertbackground="white")
        self.base_url_entry.pack(fill="x", pady=15, ipady=5)
        add_btn = tk.Button(base_frame, text="➕ Adicionar Nova Rota", command=self.add_route_frame,
                            bg="#03DAC6", fg="black", font=("Source Code Pro", 11, "bold"), padx=10, pady=5)
        add_btn.pack(pady=5, anchor="e")
        
    
        self.routes_frame = tk.Frame(self.routes_container, bg="#121212")
        self.routes_frame.pack(fill="x", padx=10)
        
    def add_route_frame(self):
    
        if not hasattr(self, 'route_count'):
            self.route_count = 0

        row = self.route_count // 2
        col = self.route_count % 2

        frame = tk.Frame(self.routes_frame, pady=10, padx=10, relief=tk.RIDGE, bd=2, bg="#1e1e1e")
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        self.routes_frame.grid_columnconfigure(col, weight=1)

        row1 = tk.Frame(frame, bg="#1e1e1e")
        row1.pack(fill='x', pady=5)

        tk.Label(row1, text="Método:", font=("Segoe UI", 11), bg="#1e1e1e", fg="white").pack(side="left")
        method = ttk.Combobox(row1, values=["GET", "POST", "PUT", "DELETE"], width=12, font=("Segoe UI", 15))
        method.set("GET")
        method.pack(side="left", padx=5)

        tk.Label(row1, text="Rota:", font=("Segoe UI", 18), bg="#1e1e1e", fg="white").pack(side="left", padx=(20, 5))
        route_entry = tk.Entry(row1, width=60, font=("Segoe UI", 18), bg="#2e2e2e", fg="white", insertbackground="white")
        route_entry.pack(side="left", expand=True, fill='x')

        tk.Label(frame, text="Headers (JSON):", anchor='w', font=("Segoe UI", 11), bg="#1e1e1e", fg="white").pack(fill='x')
        headers_text = scrolledtext.ScrolledText(frame, width=100, height=10, font=("Courier", 11),
                                                bg="#2e2e2e", fg="white", insertbackground="white", padx=5, pady=5, undo=True)
        headers_text.pack(pady=2, fill='x', expand=True)
        headers_text.bind("<KeyRelease>", lambda e: self.highlight_json_live(headers_text))
        self.highlight_json_live(headers_text)

        tk.Label(frame, text="Payload (JSON):", anchor='w', font=("Segoe UI", 11), bg="#1e1e1e", fg="white").pack(fill='x')
        payload_text = scrolledtext.ScrolledText(frame, width=100, height=10, font=("Courier", 11),
                                                bg="#2e2e2e", fg="white", insertbackground="white", padx=5, pady=5, undo=True)
        payload_text.pack(pady=2, fill='x', expand=True)
        payload_text.bind("<KeyRelease>", lambda e: self.highlight_json_live(payload_text))
        self.highlight_json_live(payload_text)

        expand_button = tk.Button(frame, text="📝 Expandir Payload", bg="#4CAF50", fg="white",
                                font=("Segoe UI", 10, "bold"), padx=10, pady=3,
                                command=lambda: self.expand_payload_popup(payload_text))
        expand_button.pack(anchor='e', pady=(0, 5))

        status_label = tk.Label(frame, text="", fg="#03DAC6", bg="#1e1e1e", anchor='w', font=("Segoe UI", 10, "bold"))
        status_label.pack(anchor='w', pady=(5, 0))

        buttons_frame = tk.Frame(frame, bg="#1e1e1e")
        buttons_frame.pack(fill='x', pady=5)

        send_button = tk.Button(buttons_frame, text="🚀 Enviar Requisição", bg="#BB86FC", fg="black",
                                font=("Segoe UI", 11, "bold"), padx=10, pady=5,
                                command=lambda: self.send_request_threaded(
                                    method.get(), route_entry.get(),
                                    headers_text.get("1.0", tk.END),
                                    payload_text.get("1.0", tk.END),
                                    status_label, response_area
                                ))
        send_button.pack(side="left", padx=5)

        clear_button = tk.Button(buttons_frame, text="🗑 Limpar Resposta", bg="#FF9800", fg="black",
                                font=("Segoe UI", 11, "bold"), padx=10, pady=5,
                                command=lambda: response_area.delete("1.0", tk.END))
        clear_button.pack(side="left", padx=5)

        remove_button = tk.Button(buttons_frame, text="❌ Remover Rota", bg="#D32F2F", fg="white",
                                font=("Segoe UI", 11, "bold"), padx=10, pady=5,
                                command=lambda: self.remove_route_frame(frame))
        remove_button.pack(side="right", padx=5)

        tk.Label(frame, text="📨 Resposta:", anchor='w', font=("Segoe UI", 11, "bold"), bg="#1e1e1e", fg="white").pack(fill='x')
        response_area = scrolledtext.ScrolledText(frame, width=100, height=7, font=("Courier", 12),
                                                bg="#1e1e1e", fg="#00ff90", insertbackground="white", padx=10, pady=5, undo=True)
        response_area.pack(pady=5, fill='x', expand=True)

        expand_response_btn = tk.Button(frame, text="🔍 Expandir Resposta", bg="#4CAF50", fg="white",
                                        font=("Segoe UI", 10, "bold"), padx=10, pady=3,
                                        command=lambda: self.expand_response_popup(response_area))
        expand_response_btn.pack(anchor='e', pady=(0, 5))
        
        tk.Label(frame, text="🤖 Resposta da IA:", anchor='w', font=("Segoe UI", 11, "bold"), bg="#1e1e1e", fg="white").pack(fill='x')
        ia_response_area = scrolledtext.ScrolledText(frame, width=100, height=7, font=("Courier", 12),
                                                    bg="#1e1e1e", fg="#42A5F5", insertbackground="white", padx=10, pady=5, undo=True)
        ia_response_area.pack(pady=5, fill='x', expand=True)

        ia_btn = tk.Button(frame, text="🤖 Resposta da IA", bg="#2196F3", fg="white",
                        font=("Segoe UI", 10, "bold"), padx=10, pady=3,
                        command=lambda: self.analisar_resposta_com_ia(
                            route_entry.get(),
                            payload_text.get("1.0", tk.END),
                            response_area.get("1.0", tk.END),
                            ia_response_area
                        ))
        ia_btn.pack(anchor='e', pady=(0, 10))
        expand_ia_btn = tk.Button(frame, text="🔍 Expandir Resposta da IA", bg="#4CAF50", fg="white",
                                font=("Segoe UI", 10, "bold"), padx=10, pady=3,
                                command=lambda: self.expand_response_popup(ia_response_area))
        expand_ia_btn.pack(anchor='e', pady=(0, 5))

        
    
        self.route_count += 1

    def remove_route_frame(self, frame):
        frame.destroy()
        self.route_count -= 1  


        self.reorganize_routes()
        
    def reorganize_routes(self):

        route_frames = [child for child in self.routes_frame.winfo_children() if isinstance(child, tk.Frame)]


        for widget in self.routes_frame.winfo_children():
            widget.grid_forget()

     
        if len(route_frames) == 1:
            route_frames[0].grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
            self.routes_frame.grid_columnconfigure(0, weight=1)
            self.routes_frame.grid_columnconfigure(1, weight=0) 
        else:
       
            for index, frame in enumerate(route_frames):
                row = index // 2
                col = index % 2
                frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

      
            self.routes_frame.grid_columnconfigure(0, weight=1)
            self.routes_frame.grid_columnconfigure(1, weight=1)    
        

    def send_request_threaded(self, method, route, headers_raw, payload_raw, status_label, response_area):
        thread = threading.Thread(
            target=self.send_single_request,
            args=(method, route, headers_raw, payload_raw, status_label, response_area),
            daemon=True
        )
        thread.start()

    def send_single_request(self, method, route, headers_raw, payload_raw, status_label, response_area):
        self.set_status(status_label, "⏳ Aguardando resposta...")
        response_area.delete("1.0", tk.END)

        base_url = self.base_url_entry.get().strip()
        url = f"{base_url.rstrip('/')}/{route.lstrip('/')}"
        headers = {}
        payload = {}
        params = {}

        try:
            if headers_raw.strip():
                headers = json.loads(headers_raw)
            if payload_raw.strip():
                payload = json.loads(payload_raw)
        except json.JSONDecodeError as e:
            self.set_status(status_label, "❌ Erro de JSON")
            messagebox.showerror("Erro de JSON", f"Erro ao interpretar headers ou payload:\n{e}")
            return

        if method.upper() in ["GET", "DELETE"]:
            params = payload
            payload = None  

        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                json=payload,
                params=params
            )
            self.set_status(status_label, f"✅ Resposta recebida! - Status Code: {response.status_code}")
            try:
                json_data = response.json()
                formatted = json.dumps(json_data, indent=4, ensure_ascii=False)
                self.highlight_json(response_area, formatted)
                
            except ValueError:
                response_area.insert(tk.END, response.text + "\n")
                
            response_area.see(tk.END)
            
        except Exception as e:
            self.set_status(status_label, "❌ Erro na requisição - resposta vazia ou falha na conexão")
            response_area.delete("1.0", tk.END)
            response_area.insert(tk.END, f"Erro: {str(e)}")
            response_area.insert(tk.END, f"Erro ao fazer requisição para {url}:\n{e}\n")
            response_area.see(tk.END)
            
    def expand_response_popup(self, response_text_widget):
        popup = tk.Toplevel(self.root)
        popup.title("Resposta Completa")
        popup.configure(bg="#121212")
        popup.geometry("900x600")
        popup.grab_set()

        tk.Label(popup, text="📨 Resposta Completa", font=("Source Code Pro", 16, "bold"),
                bg="#121212", fg="white").pack(pady=10)

        text_area = scrolledtext.ScrolledText(popup, font=("Courier", 12), bg="#1e1e1e",
                                            fg="white", insertbackground="white", wrap="word")
        text_area.pack(expand=True, fill="both", padx=20, pady=10)


        content = response_text_widget.get("1.0", tk.END)

        try:

            json_obj = json.loads(content)
            pretty = json.dumps(json_obj, indent=4, ensure_ascii=False)
            self.highlight_json(text_area, pretty)
        except Exception:
            text_area.insert("1.0", content)  

        tk.Button(popup, text="❌ Fechar", command=popup.destroy,
                bg="#D32F2F", fg="white", font=("Source Code Pro", 11, "bold"),
                padx=10, pady=5).pack(pady=10)
    
    def expand_payload_popup(self, original_text_widget):
        popup = tk.Toplevel(self.root)
        popup.title("Editor de Payload")
        popup.configure(bg="#121212")
        popup.geometry("900x600")
        popup.grab_set()  

        tk.Label(popup, text="📝 Editor de Payload", font=("Source Code Pro", 16, "bold"),
                bg="#121212", fg="white").pack(pady=10)

        text_area = scrolledtext.ScrolledText(
            popup, font=("Courier", 12), bg="#1e1e1e",
            fg="white", insertbackground="white", wrap=tk.WORD, undo=True
        )
        text_area.pack(expand=True, fill="both", padx=20, pady=10)
        
        text_area.insert("1.0", original_text_widget.get("1.0", tk.END))

        def on_mousewheel(event):
            text_area.yview_scroll(-1 * int(event.delta / 120), "units")
            return "break"

        def bind_scroll():
            text_area.bind("<MouseWheel>", on_mousewheel)

        def unbind_scroll():
            text_area.unbind("<MouseWheel>")

        text_area.bind("<Enter>", lambda e: bind_scroll())
        text_area.bind("<Leave>", lambda e: unbind_scroll())

        salvar_btn = tk.Button(
            popup, text="💾 Salvar e Fechar", command=lambda: (
                original_text_widget.delete("1.0", tk.END),
                original_text_widget.insert("1.0", text_area.get("1.0", tk.END)),
                popup.destroy()
            ),
            bg="#03DAC6", fg="black", font=("Source Code Pro", 11, "bold"),
            padx=10, pady=5
        )
        salvar_btn.pack(pady=10)
        
    def highlight_json(self, widget, json_text):
        widget.configure(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert("1.0", json_text)

        for tag in widget.tag_names():
            widget.tag_delete(tag)

        widget.tag_configure("key", foreground="yellow")
        widget.tag_configure("string", foreground="lightgreen")
        widget.tag_configure("number", foreground="hot pink")
        widget.tag_configure("boolean", foreground="deepskyblue")  

        import re

        patterns = {
            "key": r'"(.*?)"\s*:',
            "string": r':\s*"(.*?)"',
            "number": r':\s*([\d.]+)',
            "boolean": r':\s*(true|false)', 
        }

        for tag, pattern in patterns.items():
            for match in re.finditer(pattern, json_text, re.IGNORECASE):
                start_idx = match.start(1)
                end_idx = match.end(1)
                start = f"1.0+{start_idx}c"
                end = f"1.0+{end_idx}c"
                widget.tag_add(tag, start, end)

        widget.configure(state="disabled")
                
    def highlight_json_live(self, widget):
        widget.tag_remove("key", "1.0", tk.END)
        widget.tag_remove("string", "1.0", tk.END)
        widget.tag_remove("number", "1.0", tk.END)
        widget.tag_remove("boolean", "1.0", tk.END)

        text = widget.get("1.0", tk.END)

        widget.tag_config("key", foreground="#FFD700")      
        widget.tag_config("string", foreground="#7CFC00")   
        widget.tag_config("number", foreground="#FF69B4")  
        widget.tag_config("boolean", foreground="#00BFFF") 

        try:
            import re
            for match in re.finditer(r'"(.*?)"\s*:', text):
                start, end = match.span(1)
                widget.tag_add("key", f"1.0+{start}c", f"1.0+{end}c")

            for match in re.finditer(r':\s*"([^"]*?)"', text):
                start, end = match.span(1)
                widget.tag_add("string", f"1.0+{start}c", f"1.0+{end}c")

            for match in re.finditer(r':\s*(\d+(\.\d+)?)', text):
                start, end = match.span(1)
                widget.tag_add("number", f"1.0+{start}c", f"1.0+{end}c")

            for match in re.finditer(r':\s*(true|false)', text, re.IGNORECASE):
                start, end = match.span(1)
                widget.tag_add("boolean", f"1.0+{start}c", f"1.0+{end}c")

        except Exception as e:
            pass
        
    def analisar_resposta_com_ia(self, url, payload, resposta, ia_response_area):
        try:
            prompt = f"""Você é um assistente que ajuda a identificar erros em requisições de API.
    URL da rota: {url}
    Payload enviado: {payload}
    Resposta da API: {resposta}

    Analise o problema e sugira como corrigir."""
            
            resposta_ia = self.enviar_para_openrouter(prompt)

            ia_response_area.delete("1.0", tk.END)
            ia_response_area.insert(tk.END, resposta_ia)

        except Exception as e:
            ia_response_area.delete("1.0", tk.END)
            ia_response_area.insert(tk.END, f"Erro ao usar a IA: {str(e)}")
            
    def enviar_para_openrouter(self, prompt):
       
        
        headers = {
            "Authorization": f"Bearer {open_ia_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost", 
            "X-Title": "Teste API com IA"
        }

        data = {
            "model": "openai/gpt-3.5-turbo", 
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

        if response.status_code == 200:
            resposta_ia = response.json()["choices"][0]["message"]["content"]
            return resposta_ia.strip()
        else:
            raise Exception(f"Erro ao usar a IA: Error code: {response.status_code} - {response.text}")
    
    def mostrar_popup_ia(self, texto):
        popup = tk.Toplevel(self.root)
        popup.title("🔍 Análise da IA")
        popup.configure(bg="#121212")
        popup.geometry("700x500")

        tk.Label(popup, text="🤖 Sugestão da IA", font=("Segoe UI", 16, "bold"),
                bg="#121212", fg="white").pack(pady=10)

        txt = scrolledtext.ScrolledText(popup, font=("Courier", 12), bg="#1e1e1e",
                                        fg="white", insertbackground="white")
        txt.insert("1.0", texto)
        txt.configure(state="disabled")
        txt.pack(expand=True, fill="both", padx=20, pady=10)

        tk.Button(popup, text="Fechar", command=popup.destroy,
                bg="#03DAC6", fg="black", font=("Segoe UI", 10, "bold")).pack(pady=10)


    def analisar_resposta_com_ia(self, rota, payload, resposta, ia_text_widget):
        ia_text_widget.delete("1.0", tk.END)
        ia_text_widget.insert("1.0", "🤖 Aguardando resposta da IA...\n")
        thread = threading.Thread(
            target=self.enviar_para_openrouter_thread,
            args=(rota, payload, resposta, ia_text_widget)
        )
        thread.start()
        
    def enviar_para_openrouter_thread(self, rota, payload, resposta, ia_text_widget):
        try:
            prompt = f"""
    Você é um assistente especialista em APIs REST.

    Analise a resposta abaixo, considerando a rota chamada e o payload (se houver).

    Rota: {rota}

    Payload:
    {payload}

    Resposta da API:
    {resposta}

    Explique o que deu errado e sugira o que pode ser corrigido no payload ou na chamada.
    """
            headers = {
                "Authorization": f"Bearer {open_ia_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "openai/gpt-3.5-turbo", 
                "messages": [{"role": "user", "content": prompt}]
            }

            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            resposta_ia = response.json()["choices"][0]["message"]["content"]

            ia_text_widget.delete("1.0", tk.END)
            ia_text_widget.insert("1.0", resposta_ia)
        except Exception as e:
            ia_text_widget.delete("1.0", tk.END)
            ia_text_widget.insert("1.0", f"Erro ao usar a IA:\n{str(e)}")
            
    def set_status(self, label, text):
        label.config(text=text)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = APISwaggerDevelopment(root)
    root.mainloop()
