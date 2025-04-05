import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import requests
import json
import threading
import re
open_ia_key = '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'

class APISwaggerDevelopment:
    def __init__(self, root):
        self.root = root
        self.root.title("Swagger de API-test")
        self.route_frames = []
        self.routes = []
        self.char_map = {
            '"': '"',
            "'": "'",
            '{': '}',
            '[': ']'
        }
    
        self.root.configure(bg="#121212")
        self.root.state("zoomed")  
        self.create_widgets()

    def create_widgets(self):
        bg_main = "#121212"
        bg_input = "#1E1E1E"
        fg_text = "#FFFFFF"
        border_color = "#2A2A2A"
        accent_color = "#03DAC6"
        accent_hover = "#00BFA6"

        self.root.configure(bg=bg_main)

        main_frame = tk.Frame(self.root, bg=bg_main)
        main_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(main_frame, bg=bg_main, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)

        self.routes_container = tk.Frame(canvas, bg=bg_main)
        self.routes_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", _on_mousewheel)
        canvas.bind_all("<Button-5>", _on_mousewheel)

        self.window_item = canvas.create_window((0, 0), window=self.routes_container, anchor="n")

        def on_canvas_configure(event):
            canvas.itemconfig(self.window_item, width=event.width)
            canvas.coords(self.window_item, event.width / 2, 0)
        canvas.bind("<Configure>", on_canvas_configure)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        base_frame = tk.Frame(self.routes_container, pady=10, bg=bg_main)
        base_frame.pack(fill="x", padx=20)

        tk.Label(
            base_frame,
            text="🔗 Base da API:",
            font=("Source Code Pro", 18, "bold"),
            bg=bg_main,
            fg=fg_text
        ).pack(anchor="w")

        self.base_url_entry = tk.Entry(
            base_frame,
            font=("Source Code Pro", 16),
            bg=bg_input,
            fg=fg_text,
            insertbackground=fg_text,
            highlightthickness=1,
            relief="flat",
            highlightbackground=border_color,
            highlightcolor=accent_color
        )
        self.base_url_entry.pack(fill="x", pady=10, ipady=8)

        add_btn = tk.Button(
            base_frame,
            text="➕ Adicionar Nova Rota",
            command=self.add_route_frame,
            bg=accent_color,
            fg="black",
            font=("Source Code Pro", 12, "bold"),
            activebackground=accent_hover,
            activeforeground="black",
            padx=12,
            pady=6,
            relief="flat",
            bd=0,
            cursor="hand2"
        )
        add_btn.pack(pady=5, anchor="e")

        self.routes_frame = tk.Frame(self.routes_container, bg=bg_main)
        self.routes_frame.pack(fill="x", padx=10)
        
    def add_route_frame(self):

        entry_bg = "#ffffff"       
        entry_fg = "#000000"       
        button_font = ("Segoe UI", 10, "bold")
        
        btn_primary_bg = "#6200EE"
        btn_primary_fg = "white"

        btn_success_bg = "#2E7D32"
        btn_success_fg = "white"

        btn_warn_bg = "#FFA000"
        btn_warn_fg = "black"

        btn_danger_bg = "#C62828"
        btn_danger_fg = "white"

        btn_ai_bg = "#2962FF"
        btn_ai_fg = "white"
        
        bg_card = "#1e1e1e"  
        fg_label = "white" 
        
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

        tk.Label(frame, text="Headers (JSON):", anchor='w', font=("Segoe UI", 11, "bold"), bg=bg_card, fg=fg_label).pack(fill='x')
        headers_text = scrolledtext.ScrolledText(
            frame, width=100, height=8, font=("Courier New", 11),
            bg="#2e2e2e", fg="white", insertbackground="white",
            padx=12, pady=8, bd=0, relief="flat", undo=True,
            highlightthickness=1, highlightbackground="#444", highlightcolor="#888"
        )
        
        headers_text.pack(pady=5, fill='x', expand=True)
        headers_text.pack(pady=2, fill='x', expand=True)
        headers_text.bind("<KeyRelease>", lambda e: self.highlight_json_live(headers_text))
        self.highlight_json_live(headers_text)

        tk.Label(frame, text="Payload (JSON):", anchor='w', font=("Segoe UI", 11, "bold"), bg=bg_card, fg=fg_label).pack(fill='x')
        payload_text = scrolledtext.ScrolledText(
            frame, width=100, height=8, font=("Courier New", 11),
            bg="#2e2e2e", fg="white", insertbackground="white",
            padx=12, pady=8, bd=0, relief="flat", undo=True,
            highlightthickness=1, highlightbackground="#444", highlightcolor="#888"
        )
        payload_text.pack(pady=5, fill='x', expand=True)
        
        
        payload_text.bind("<KeyRelease>", lambda e: self.highlight_json_live(payload_text))
        self.highlight_json_live(payload_text)
        
        headers_text.bind("<KeyRelease>", lambda e: self.highlight_json_live(headers_text))
        payload_text.bind("<KeyRelease>", lambda e: self.highlight_json_live(payload_text))
        
        headers_text.bind("<FocusOut>", lambda e: self.formatar_json_auto(headers_text))
        payload_text.bind("<FocusOut>", lambda e: self.formatar_json_auto(payload_text))
        
        headers_text.bind('"', lambda e: self.handle_quote(e, headers_text))
        payload_text.bind('"', lambda e: self.handle_quote(e, payload_text))
        headers_text.bind("<BackSpace>", lambda e: self.handle_custom_delete(e, headers_text))
        headers_text.bind("<Delete>", lambda e: self.handle_custom_delete(e, headers_text))
        payload_text.bind("<BackSpace>", lambda e: self.handle_custom_delete(e, payload_text))
        payload_text.bind("<Delete>", lambda e: self.handle_custom_delete(e, payload_text))

        for char in ['"', "'", '{', '[']:
            headers_text.bind(char, lambda e, w=headers_text, c=char: self.auto_fechar(e, w, c))
            payload_text.bind(char, lambda e, w=payload_text, c=char: self.auto_fechar(e, w, c))
            
        expand_button = tk.Button(frame, text="📝 Expandir Payload", bg="#4CAF50", fg="white",
                                font=("Segoe UI", 10, "bold"), padx=10, pady=3,
                                command=lambda: self.expand_payload_popup(payload_text))
        expand_button.pack(anchor='e', pady=(0, 5))

        status_label = tk.Label(frame, text="", fg="#03DAC6", bg="#1e1e1e", anchor='w', font=("Segoe UI", 10, "bold"))
        status_label.pack(anchor='w', pady=(5, 0))

        buttons_frame = tk.Frame(frame, bg="#1e1e1e")
        buttons_frame.pack(fill='x', pady=5)

        send_button = tk.Button(
            buttons_frame, text="🚀 Enviar Requisição",
            bg=btn_primary_bg, fg=btn_primary_fg,
            font=button_font, padx=12, pady=6,
            command=lambda: self.send_request_threaded(
                method.get(), route_entry.get(),
                headers_text.get("1.0", tk.END),
                payload_text.get("1.0", tk.END),
                status_label, response_area
            )
        )
        send_button.pack(side="left", padx=5)

        clear_button = tk.Button(
            buttons_frame, text="🗑 Limpar Resposta",
            bg=btn_warn_bg, fg=btn_warn_fg,
            font=button_font, padx=12, pady=6,
            command=lambda: self.limpar_resposta(response_area, status_label)
        )
        clear_button.pack(side="left", padx=5)

        remove_button = tk.Button(
            buttons_frame, text="❌ Remover Rota",
            bg=btn_danger_bg, fg=btn_danger_fg,
            font=button_font, padx=12, pady=6,
            command=lambda: self.remove_route_frame(frame)
        )
        remove_button.pack(side="right", padx=5)

        tk.Label(frame, text="📨 Resposta:", anchor='w', font=("Segoe UI", 11, "bold"), bg=bg_card, fg=fg_label).pack(fill='x')
        response_area = scrolledtext.ScrolledText(
            frame, width=100, height=7, font=("Courier", 12),
            bg="#1e1e1e", fg="#00ff90", insertbackground="white",
            padx=12, pady=8, bd=0, relief="flat", undo=True,
            highlightthickness=1, highlightbackground="#444", highlightcolor="#00ff90"
        )
        response_area.pack(pady=5, fill='x', expand=True)

        expand_response_btn = tk.Button(
            frame, text="🔍 Expandir Resposta",
            bg=btn_success_bg, fg=btn_success_fg,
            font=button_font, padx=12, pady=4,
            command=lambda: self.expand_response_popup(response_area)
        )
        expand_response_btn.pack(anchor='e', pady=(0, 5))
        
        tk.Label(frame, text="🤖 Inteligência Artificial:", anchor='w', font=("Segoe UI", 11, "bold"), bg=bg_card, fg=fg_label).pack(fill='x')
        ia_response_area = scrolledtext.ScrolledText(
            frame, width=100, height=7, font=("Courier", 12),
            bg="#1e1e1e", fg="#42A5F5", insertbackground="white",
            padx=12, pady=8, bd=0, relief="flat", undo=True,
            highlightthickness=1, highlightbackground="#444", highlightcolor="#42A5F5"
        )
        ia_response_area.pack(pady=5, fill='x', expand=True)
        

        ia_btn = tk.Button(
            frame, text="Solução de Erro",
            bg=btn_ai_bg, fg=btn_ai_fg,
            font=button_font, padx=12, pady=4,
            command=lambda: self.analisar_resposta_com_ia(
                route_entry.get(),
                payload_text.get("1.0", tk.END),
                response_area.get("1.0", tk.END),
                ia_response_area
            )
        )
        ia_btn.pack(anchor='e', pady=(0, 5))
        
        expand_ia_btn = tk.Button(
            frame, text="🔍 Expandir Resposta da IA",
            bg=btn_success_bg, fg=btn_success_fg,
            font=button_font, padx=12, pady=4,
            command=lambda: self.expand_response_popup_ia(ia_response_area)
        )
        expand_ia_btn.pack(anchor='e', pady=(0, 10))
        self.route_frames.append(frame)
        self.reorganize_routes()
        
        self.route_count += 1
        
    def remove_route_frame(self, frame):
        frame.destroy()
        if frame in self.route_frames:
            self.route_frames.remove(frame)
        self.reorganize_routes()


    def reorganize_routes(self):
        for widget in self.routes_frame.winfo_children():
            widget.grid_forget()

        total = len(self.route_frames)

        if total == 1:
            self.route_frames[0].grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
            self.routes_frame.grid_columnconfigure(0, weight=1)
            self.routes_frame.grid_columnconfigure(1, weight=0)
        else:
            for index, frame in enumerate(self.route_frames):
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

        text_area = scrolledtext.ScrolledText(
            popup,
            font=("Courier", 12),
            bg="#1e1e1e",
            fg="white",
            insertbackground="white",
            wrap="word"
        )
        text_area.pack(expand=True, fill="both", padx=20, pady=10)

        content = response_text_widget.get("1.0", tk.END)

        try:
            json_obj = json.loads(content)
            pretty = json.dumps(json_obj, indent=4, ensure_ascii=False)
            self.highlight_json(text_area, pretty)
        except Exception:
            
            # Texto simples, aplica verde
            text_area.insert("1.0", content)
            text_area.tag_config("green_text", foreground="#00ff90")
            text_area.tag_add("green_text", "1.0", tk.END)

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

        self.highlight_json_live(text_area)
        self.formatar_json_auto(text_area)
        
        text_area.bind("<KeyRelease>", lambda e: [
            self.highlight_json_live(text_area),
            self.formatar_json_auto(text_area)
        ])
        text_area.bind('"', lambda e: self.handle_quote(e, text_area))
        text_area.bind("<BackSpace>", lambda e: self.handle_custom_delete(e, text_area))
        text_area.bind("<Delete>", lambda e: self.handle_custom_delete(e, text_area))

        text_area.bind("<Enter>", lambda e: text_area.bind("<MouseWheel>", lambda ev: text_area.yview_scroll(-1 * int(ev.delta / 120), "units")))
        text_area.bind("<Leave>", lambda e: text_area.unbind("<MouseWheel>"))

        def salvar_e_fechar():
            novo_texto = text_area.get("1.0", tk.END)
            original_text_widget.delete("1.0", tk.END)
            original_text_widget.insert("1.0", novo_texto)

  
            self.highlight_json_live(original_text_widget)
            popup.destroy()

        salvar_btn = tk.Button(
            popup, text="💾 Salvar e Fechar", command=salvar_e_fechar,
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
        
        for tag in ["key", "string", "number", "boolean", "null", "brace"]:
            widget.tag_remove(tag, "1.0", tk.END)

        text = widget.get("1.0", tk.END)

      
        widget.tag_config("key", foreground="#4FC3F7")     
        widget.tag_config("string", foreground="#66BB6A")   
        widget.tag_config("number", foreground="#FF69B4")   
        widget.tag_config("boolean", foreground="#A0522D")  
        widget.tag_config("null", foreground="#A0522D")    
        widget.tag_config("brace", foreground="#FFD700")    

        try:
            
            for match in re.finditer(r'(".*?")\s*:', text):
                start, end = match.span(1)
                widget.tag_add("key", f"1.0+{start}c", f"1.0+{end}c")

            
            for match in re.finditer(r':\s*(".*?")', text):
                start, end = match.span(1)
                widget.tag_add("string", f"1.0+{start}c", f"1.0+{end}c")

          
            for match in re.finditer(r':\s*(-?\d+(\.\d+)?)', text):
                start, end = match.span(1)
                widget.tag_add("number", f"1.0+{start}c", f"1.0+{end}c")

            for match in re.finditer(r':\s*(true|false)', text, re.IGNORECASE):
                start, end = match.span(1)
                widget.tag_add("boolean", f"1.0+{start}c", f"1.0+{end}c")

        
            for match in re.finditer(r':\s*(null)', text, re.IGNORECASE):
                start, end = match.span(1)
                widget.tag_add("null", f"1.0+{start}c", f"1.0+{end}c")

            for match in re.finditer(r'[{}\[\]]', text):
                start = match.start()
                end = match.end()
                widget.tag_add("brace", f"1.0+{start}c", f"1.0+{end}c")

        except Exception:
            pass
    def limpar_resposta(self, response_area, status_label):
        response_area.delete("1.0", tk.END)
        status_label.config(text="") 
        
            
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
    
    def expand_response_popup_ia(self, ia_response_area):
        popup = tk.Toplevel(self.root)
        popup.title("🔍 Análise da IA")
        popup.configure(bg="#121212")
        popup.geometry("700x500")

        tk.Label(popup, text="🤖 Sugestão da IA", font=("Segoe UI", 16, "bold"),
                bg="#121212", fg="white").pack(pady=10)

        txt = scrolledtext.ScrolledText(popup, font=("Courier", 12), bg="#1e1e1e",
                                        fg="white", insertbackground="white")
        txt.pack(expand=True, fill="both", padx=20, pady=10)

        texto = ia_response_area.get("1.0", tk.END)

        txt.delete("1.0", tk.END)  
        txt.insert("1.0", texto)
        self.colorir_resposta_ia(txt)

        txt.configure(state="disabled")

        tk.Button(popup, text="Fechar", command=popup.destroy,
                bg="#03DAC6", fg="black", font=("Segoe UI", 10, "bold")).pack(pady=10)
    def analisar_resposta_com_ia(self, rota, payload, resposta, ia_text_widget):
        ia_text_widget.configure(state="normal")
        ia_text_widget.delete("1.0", tk.END)
        ia_text_widget.insert("1.0", "Aguardando resposta...\n")
        ia_text_widget.configure(state="disabled")

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

            Explique o que deu errado e sugira o que pode ser corrigido no payload ou na chamada, também quero um exemplo do payload ou chamada.
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

            ia_text_widget.configure(state="normal")
            ia_text_widget.delete("1.0", tk.END)
            ia_text_widget.insert("1.0", resposta_ia)
            ia_text_widget.configure(state="disabled")

        except Exception as e:
            ia_text_widget.configure(state="normal")
            ia_text_widget.delete("1.0", tk.END)
            ia_text_widget.insert("1.0", f"Erro ao usar a IA:\n{str(e)}")
            ia_text_widget.configure(state="disabled")
        
    def handle_quote(self, event, text_widget):
        try:
            sel_start = text_widget.index("sel.first")
            sel_end = text_widget.index("sel.last")
            selected_text = text_widget.get(sel_start, sel_end)
            
        
            text_widget.delete(sel_start, sel_end)
            text_widget.insert(sel_start, f'"{selected_text}"')
            
            return "break"  
        except tk.TclError:
            
            cursor_pos = text_widget.index(tk.INSERT)
            text_widget.insert(cursor_pos, '""')
            text_widget.mark_set(tk.INSERT, f"{cursor_pos}+1c")  
            
            return "break" 
        
    def handle_custom_delete(self, event, text_widget):
        try:
            sel_start = text_widget.index("sel.first")
            sel_end = text_widget.index("sel.last")
            selected_text = text_widget.get(sel_start, sel_end)

            before = text_widget.get(f"{sel_start} -1c")
            after = text_widget.get(sel_end)

            if (before == '"' and after == '"') or (before in ':{[,' and after in '}],'):
                text_widget.delete(sel_start, sel_end)
                return "break"

        except tk.TclError:
            pass  

    def colorir_resposta_ia(self, widget):
        widget.tag_config("chave", foreground="#FFEB3B") 
        widget.tag_config("valor", foreground="#4CAF50") 
        widget.tag_config("erro", foreground="#F44336")  
        widget.tag_config("info", foreground="#2196F3")  

        texto = widget.get("1.0", tk.END)

        widget.tag_remove("chave", "1.0", tk.END)
        widget.tag_remove("valor", "1.0", tk.END)
        widget.tag_remove("erro", "1.0", tk.END)
        widget.tag_remove("info", "1.0", tk.END)

        for idx, linha in enumerate(texto.splitlines(), 1):
            if "erro" in linha.lower():
                widget.tag_add("erro", f"{idx}.0", f"{idx}.end")
            elif "exemplo" in linha.lower():
                widget.tag_add("valor", f"{idx}.0", f"{idx}.end")
            elif ":" in linha:
                widget.tag_add("chave", f"{idx}.0", f"{idx}.end")
            else:
                widget.tag_add("info", f"{idx}.0", f"{idx}.end")
                
    def exibir_resposta_ia_formatada(self, widget, texto):
        widget.configure(state='normal')
        widget.delete("1.0", tk.END)
        widget.insert("1.0", texto)

        # Cores vivas
        widget.tag_config("titulo", foreground="#FFD700", font=("Courier", 12, "bold"))  
        widget.tag_config("solucao", foreground="#00FF00", font=("Courier", 11))        
        widget.tag_config("erro", foreground="#FF4C4C", font=("Courier", 11, "bold"))    
        widget.tag_config("info", foreground="#00E5FF", font=("Courier", 11))          

        palavras_chave = {
            "Erro": "erro",
            "error": "erro",
            "Solução": "solucao",
            "Solução sugerida": "solucao",
            "Sugestão": "solucao",
            "Recomenda": "solucao",
            "Dica": "info",
            "Possível causa": "titulo",
            "Análise da resposta": "titulo",
            "Resposta da IA": "titulo",
        }

        for palavra, tag in palavras_chave.items():
            start = "1.0"
            while True:
                pos = widget.search(palavra, start, tk.END, nocase=True)
                if not pos:
                    break
                end = f"{pos}+{len(palavra)}c"
                widget.tag_add(tag, pos, end)
                start = end

        widget.configure(state='disabled')
        
    def formatar_json_auto(self, widget):
        def delayed_format():
            raw = widget.get("1.0", "end-1c").strip()
            if not raw:
                return

            bonito = self.corrigir_json_rapido(raw)

            if bonito != raw:
                widget.delete("1.0", tk.END)
                widget.insert("1.0", bonito)
                self.highlight_json_live(widget)

        if hasattr(widget, "_debounce_timer") and widget._debounce_timer is not None:
            widget._debounce_timer.cancel()

        widget._debounce_timer = threading.Timer(1.0, delayed_format)
        widget._debounce_timer.start()
        
    def corrigir_json_rapido(self, raw):
        raw = raw.strip()

        def adicionar_aspas_chaves(texto):

            return re.sub(r'(?<!")(\b[a-zA-Z_][\w\-]*\b)(?=\s*:)', r'"\1"', texto)

        def corrigir_virgulas(texto):
         
            texto = re.sub(r'(".*?")\s+(".*?"\s*:)', r'\1,\2', texto)
            texto = re.sub(r'(\d+)\s+(".*?"\s*:)', r'\1,\2', texto)
            return texto

        try:
            return json.dumps(json.loads(raw), indent=4, ensure_ascii=False)
        except Exception:
            pass

        try:
            temp = adicionar_aspas_chaves(raw)
            temp = corrigir_virgulas(temp)
            parsed = json.loads(temp)
            return json.dumps(parsed, indent=4, ensure_ascii=False)
        except Exception:
            pass

        try:
            import ast
            parsed = ast.literal_eval(raw)
            return json.dumps(parsed, indent=4, ensure_ascii=False)
        except Exception:
            pass

        return raw

    def auto_fechar(self, event, widget, char):
        try:

            pair = self.char_map[char]

       
            try:
                start = widget.index("sel.first")
                end = widget.index("sel.last")
                texto_selecionado = widget.get(start, end)
                widget.delete(start, end)
                widget.insert(start, f"{char}{texto_selecionado}{pair}")
                return "break"
            except tk.TclError:
                pass

            pos = widget.index(tk.INSERT)
            widget.insert(pos, f"{char}{pair}")
            widget.mark_set(tk.INSERT, f"{pos}+1c")
            return "break"

        except Exception as e:
            print(f"[Erro auto_fechar]: {e}")
    
    def set_status(self, label, text):
        label.config(text=text)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = APISwaggerDevelopment(root)
    root.mainloop()
