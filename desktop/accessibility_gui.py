import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
import time

class BrazoRoboticoCyberGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔥 BRAZO ROBÓTICO 6-DOF | CONTROL & MONITOREO")
        self.root.geometry("640x750")
        self.root.configure(bg="#0f0c1b")  # Fondo Púrpura/Neón profundo
        self.root.resizable(False, False)

        self.arduino = None
        self.leyendo = False

        self.angulos = [tk.IntVar(value=90) for _ in range(6)]
        
        # Estructura de nombres con sus colores vibrantes por articulación
        self.nombres_servos = [
            ("SERVO 1", "Base - Rotación Axial", "#ff007f", "#ff55a3"),       # Magenta Vivo
            ("SERVO 2", "Hombro - Elevación Principal", "#00f2fe", "#4facfe"), # Cian Neón
            ("SERVO 3", "Codo - Articulación Media", "#00ff87", "#60efff"),   # Verde Lima / Neón
            ("SERVO 4", "Muñeca - Elevación Pitch", "#ff9900", "#ffcc00"),   # Naranja Vibrante
            ("SERVO 5", "Muñeca - Giro Roll", "#bf00ff", "#e066ff"),          # Púrpura Eléctrico
            ("SERVO 6", "Gripper - Pinza Efector", "#ff0033", "#ff5e62")     # Rojo Fuego
        ]

        self.labels_valores = []
        self.crear_interfaz()

    def crear_interfaz(self):
        # ------------------- HEADER / ENCABEZADO -------------------
        frame_header = tk.Frame(self.root, bg="#1a1528", highlightbackground="#ff007f", highlightthickness=2)
        frame_header.pack(fill="x", padx=15, pady=(15, 10))

        lbl_titulo = tk.Label(
            frame_header, 
            text="⚡ DASHBOARD DE CONTROL ROBÓTICO ⚡", 
            font=("Segoe UI", 16, "bold"),
            bg="#1a1528",
            fg="#00f2fe"
        )
        lbl_titulo.pack(pady=(12, 2))

        lbl_sub = tk.Label(
            frame_header, 
            text="★ TELEOPERACIÓN Y ACCESIBILIDAD 6 DEGREES OF FREEDOM ★", 
            font=("Segoe UI", 9, "bold"),
            bg="#1a1528",
            fg="#ff007f"
        )
        lbl_sub.pack(pady=(0, 12))

        # ------------------- MARCO CONEXIÓN -------------------
        frame_conexion = tk.Frame(self.root, bg="#181325", highlightbackground="#00f2fe", highlightthickness=1)
        frame_conexion.pack(fill="x", padx=15, pady=5)

        lbl_port = tk.Label(frame_conexion, text="🔌 PUERTO COM:", font=("Segoe UI", 10, "bold"), bg="#181325", fg="#00ff87")
        lbl_port.pack(side="left", padx=(15, 5), pady=12)

        self.combo_puertos = ttk.Combobox(frame_conexion, width=15, state="readonly")
        self.combo_puertos.pack(side="left", padx=5)

        btn_refresh = tk.Button(
            frame_conexion, 
            text="🔄", 
            command=self.actualizar_puertos, 
            bg="#ff9900", 
            fg="black", 
            font=("Segoe UI", 10, "bold"),
            bd=0, 
            padx=10, 
            activebackground="#ffcc00",
            cursor="hand2"
        )
        btn_refresh.pack(side="left", padx=5)

        self.btn_conectar = tk.Button(
            frame_conexion, 
            text="🚀 CONECTAR", 
            command=self.toggle_conexion, 
            bg="#00ff87", 
            fg="#0f0c1b",
            font=("Segoe UI", 11, "bold"),
            bd=0,
            padx=15,
            pady=4,
            activebackground="#60efff",
            cursor="hand2"
        )
        self.btn_conectar.pack(side="right", padx=15)

        self.actualizar_puertos()

        # ------------------- TARJETAS DE SERVOS -------------------
        frame_cards = tk.Frame(self.root, bg="#0f0c1b")
        frame_cards.pack(fill="both", expand=True, padx=15, pady=10)

        for i in range(6):
            color_primario = self.nombres_servos[i][2]
            
            # Tarjeta con borde del color específico de la articulación
            card = tk.Frame(frame_cards, bg="#1c162e", highlightbackground=color_primario, highlightthickness=1.5)
            card.pack(fill="x", padx=5, pady=6)

            frame_info = tk.Frame(card, bg="#1c162e")
            frame_info.pack(fill="x", padx=12, pady=(8, 2))

            # Título del servo en color neón
            lbl_tag = tk.Label(
                frame_info, 
                text=self.nombres_servos[i][0], 
                font=("Segoe UI", 10, "bold"), 
                bg="#1c162e", 
                fg=color_primario
            )
            lbl_tag.pack(side="left")

            lbl_desc = tk.Label(
                frame_info, 
                text=f"• {self.nombres_servos[i][1]}", 
                font=("Segoe UI", 9, "bold"), 
                bg="#1c162e", 
                fg="#ffffff"
            )
            lbl_desc.pack(side="left", padx=8)

            # Badge digital super llamativo
            lbl_val = tk.Label(
                frame_info, 
                text="90°", 
                font=("Consolas", 13, "bold"), 
                bg="#000000",
                fg=color_primario,
                width=6,
                bd=1,
                relief="solid"
            )
            lbl_val.pack(side="right")
            self.labels_valores.append(lbl_val)

            # Deslizador interactivo
            slider = tk.Scale(
                card, 
                from_=0, 
                to=180, 
                orient="horizontal",
                variable=self.angulos[i],
                command=lambda val, idx=i: self.al_mover_slider(idx, val),
                bg="#1c162e",
                fg="#1c162e",
                troughcolor="#2d2249",
                activebackground=color_primario,
                highlightthickness=0,
                bd=0,
                length=580,
                showvalue=False,
                cursor="hand2"
            )
            slider.pack(fill="x", padx=12, pady=(0, 8))

        # ------------------- BARRA DE ESTADO FOOTER -------------------
        self.lbl_status = tk.Label(
            self.root, 
            text="● Estado: DESCONECTADO", 
            fg="#ff0055", 
            bg="#0f0c1b", 
            font=("Segoe UI", 10, "bold")
        )
        self.lbl_status.pack(pady=8)

    def actualizar_puertos(self):
        puertos = [port.device for port in serial.tools.list_ports.comports()]
        self.combo_puertos['values'] = puertos if puertos else ["Sin Puertos"]
        if puertos:
            self.combo_puertos.current(0)

    def toggle_conexion(self):
        if not self.leyendo:
            puerto = self.combo_puertos.get()
            if not puerto or puerto == "Sin Puertos":
                return
            try:
                self.arduino = serial.Serial(puerto, 9600, timeout=1)
                self.leyendo = True
                self.btn_conectar.config(text="🛑 DESCONECTAR", bg="#ff0055", fg="white")
                self.lbl_status.config(text=f"● Estado: CONECTADO EN {puerto}", fg="#00ff87")
                threading.Thread(target=self.leer_serial, daemon=True).start()
            except Exception as e:
                self.lbl_status.config(text=f"● Error de Conexión: {e}", fg="#ff0055")
        else:
            self.leyendo = False
            if self.arduino:
                self.arduino.close()
            self.btn_conectar.config(text="🚀 CONECTAR", bg="#00ff87", fg="#0f0c1b")
            self.lbl_status.config(text="● Estado: DESCONECTADO", fg="#ff0055")

    def al_mover_slider(self, indice, valor):
        val_int = int(float(valor))
        self.labels_valores[indice].config(text=f"{val_int}°")
        
        if self.arduino and self.arduino.is_open:
            comando = f"S{indice+1}:{val_int}\n"
            try:
                self.arduino.write(comando.encode('utf-8'))
            except Exception:
                pass

    def leer_serial(self):
        while self.leyendo and self.arduino and self.arduino.is_open:
            try:
                linea = self.arduino.readline().decode('utf-8').strip()
                if linea and "S1:" in linea:
                    partes = linea.split("|")
                    if len(partes) == 6:
                        for i in range(6):
                            val = int(partes[i].split(":")[1].strip())
                            self.angulos[i].set(val)
                            self.labels_valores[i].config(text=f"{val}°")
            except Exception:
                pass
            time.sleep(0.04)

if __name__ == "__main__":
    root = tk.Tk()
    app = BrazoRoboticoCyberGUI(root)
    root.mainloop()