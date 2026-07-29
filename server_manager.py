import os
import sys
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# =========================================================
# PATHS
# =========================================================

def get_base_folder() -> str:
    """Return the folder containing the script or compiled EXE."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.abspath(__file__))


BASE_FOLDER = get_base_folder()
JAR_FILE = os.path.join(BASE_FOLDER, "paper.jar")
PROPERTIES_FILE = os.path.join(BASE_FOLDER, "server.properties")


# =========================================================
# COLORS
# =========================================================

BACKGROUND = "#101419"
PANEL = "#181e25"
PANEL_LIGHT = "#212933"
INPUT_BACKGROUND = "#0d1117"
BORDER = "#303943"

TEXT = "#f0f4f8"
TEXT_MUTED = "#9ca9b5"

GREEN = "#53d769"
GREEN_DARK = "#2f9e44"
RED = "#ff5f57"
RED_DARK = "#c93c36"
YELLOW = "#ffbd2e"
BLUE = "#4da3ff"
BLUE_DARK = "#2878c7"


# =========================================================
# SERVER MANAGER
# =========================================================

class PaperServerManager:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.server_process: subprocess.Popen | None = None
        self.server_ready = False
        self.closing_program = False

        self.property_entries: dict[str, tk.Variable] = {}

        self.setup_window()
        self.setup_styles()
        self.create_interface()
        self.load_properties()
        self.update_status("Offline", RED)
        self.refresh_file_status()

        self.root.protocol("WM_DELETE_WINDOW", self.close_program)

    # =====================================================
    # WINDOW
    # =====================================================

    def setup_window(self) -> None:
        self.root.title("Paper Server Studio")
        self.root.geometry("1100x720")
        self.root.minsize(900, 620)
        self.root.configure(bg=BACKGROUND)

        try:
            self.root.iconbitmap(os.path.join(BASE_FOLDER, "server.ico"))
        except Exception:
            pass

    def setup_styles(self) -> None:
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Main.TNotebook",
            background=BACKGROUND,
            borderwidth=0
        )

        style.configure(
            "Main.TNotebook.Tab",
            background=PANEL,
            foreground=TEXT_MUTED,
            padding=(20, 11),
            borderwidth=0,
            font=("Segoe UI", 10, "bold")
        )

        style.map(
            "Main.TNotebook.Tab",
            background=[("selected", PANEL_LIGHT)],
            foreground=[("selected", TEXT)]
        )

        style.configure(
            "Server.TCombobox",
            fieldbackground=INPUT_BACKGROUND,
            background=INPUT_BACKGROUND,
            foreground=TEXT,
            arrowcolor=TEXT,
            bordercolor=BORDER,
            lightcolor=BORDER,
            darkcolor=BORDER,
            padding=6
        )

    # =====================================================
    # INTERFACE
    # =====================================================

    def create_interface(self) -> None:
        self.create_header()

        self.notebook = ttk.Notebook(
            self.root,
            style="Main.TNotebook"
        )
        self.notebook.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(0, 18)
        )

        self.dashboard_tab = tk.Frame(
            self.notebook,
            bg=BACKGROUND
        )

        self.settings_tab = tk.Frame(
            self.notebook,
            bg=BACKGROUND
        )

        self.advanced_tab = tk.Frame(
            self.notebook,
            bg=BACKGROUND
        )

        self.notebook.add(
            self.dashboard_tab,
            text="  Dashboard  "
        )

        self.notebook.add(
            self.settings_tab,
            text="  Server Settings  "
        )

        self.notebook.add(
            self.advanced_tab,
            text="  Advanced Editor  "
        )

        self.create_dashboard()
        self.create_settings_page()
        self.create_advanced_page()

    def create_header(self) -> None:
        header = tk.Frame(
            self.root,
            bg=BACKGROUND,
            height=85
        )
        header.pack(fill="x", padx=22, pady=(16, 8))
        header.pack_propagate(False)

        title_area = tk.Frame(header, bg=BACKGROUND)
        title_area.pack(side="left", fill="y")

        tk.Label(
            title_area,
            text="PAPER SERVER",
            bg=BACKGROUND,
            fg=TEXT,
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w")

        tk.Label(
            title_area,
            text="Minecraft 1.12.2 Control Panel",
            bg=BACKGROUND,
            fg=TEXT_MUTED,
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(2, 0))

        status_area = tk.Frame(header, bg=BACKGROUND)
        status_area.pack(side="right", padx=5)

        self.status_dot = tk.Canvas(
            status_area,
            width=18,
            height=18,
            bg=BACKGROUND,
            highlightthickness=0
        )
        self.status_dot.pack(side="left", padx=(0, 8))

        self.status_circle = self.status_dot.create_oval(
            3,
            3,
            15,
            15,
            fill=RED,
            outline=""
        )

        self.status_label = tk.Label(
            status_area,
            text="Offline",
            bg=BACKGROUND,
            fg=TEXT,
            font=("Segoe UI", 11, "bold")
        )
        self.status_label.pack(side="left")

    # =====================================================
    # DASHBOARD
    # =====================================================

    def create_dashboard(self) -> None:
        controls = tk.Frame(
            self.dashboard_tab,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        controls.pack(fill="x", pady=(8, 12))

        left_controls = tk.Frame(controls, bg=PANEL)
        left_controls.pack(side="left", padx=16, pady=14)

        self.start_button = self.create_button(
            left_controls,
            "▶  START SERVER",
            GREEN,
            GREEN_DARK,
            self.start_server,
            width=17
        )
        self.start_button.pack(side="left", padx=(0, 8))

        self.stop_button = self.create_button(
            left_controls,
            "■  STOP",
            RED,
            RED_DARK,
            self.stop_server,
            width=12
        )
        self.stop_button.pack(side="left", padx=8)

        self.restart_button = self.create_button(
            left_controls,
            "↻  RESTART",
            YELLOW,
            "#d69513",
            self.restart_server,
            width=12
        )
        self.restart_button.pack(side="left", padx=8)

        right_controls = tk.Frame(controls, bg=PANEL)
        right_controls.pack(side="right", padx=16, pady=14)

        folder_button = self.create_button(
            right_controls,
            "📁  OPEN FOLDER",
            BLUE,
            BLUE_DARK,
            self.open_server_folder,
            width=15
        )
        folder_button.pack(side="right")

        information_row = tk.Frame(
            self.dashboard_tab,
            bg=BACKGROUND
        )
        information_row.pack(fill="x", pady=(0, 12))

        self.players_card_value = self.create_info_card(
            information_row,
            "PLAYERS",
            "0 / 5"
        )

        self.ram_card_value = self.create_info_card(
            information_row,
            "MAXIMUM RAM",
            "4 GB"
        )

        self.port_card_value = self.create_info_card(
            information_row,
            "SERVER PORT",
            "25565"
        )

        self.jar_card_value = self.create_info_card(
            information_row,
            "SERVER FILE",
            "Checking..."
        )

        console_panel = tk.Frame(
            self.dashboard_tab,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        console_panel.pack(fill="both", expand=True)

        console_header = tk.Frame(
            console_panel,
            bg=PANEL_LIGHT,
            height=42
        )
        console_header.pack(fill="x")
        console_header.pack_propagate(False)

        tk.Label(
            console_header,
            text="SERVER CONSOLE",
            bg=PANEL_LIGHT,
            fg=TEXT,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=14)

        clear_button = tk.Button(
            console_header,
            text="Clear",
            command=self.clear_console,
            bg=PANEL_LIGHT,
            fg=TEXT_MUTED,
            activebackground=PANEL_LIGHT,
            activeforeground=TEXT,
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 9)
        )
        clear_button.pack(side="right", padx=12)

        self.console_box = scrolledtext.ScrolledText(
            console_panel,
            bg=INPUT_BACKGROUND,
            fg="#d8e1e8",
            insertbackground=TEXT,
            selectbackground=BLUE_DARK,
            relief="flat",
            borderwidth=0,
            wrap=tk.WORD,
            font=("Consolas", 10),
            padx=12,
            pady=12,
            state="disabled"
        )
        self.console_box.pack(
            fill="both",
            expand=True,
            padx=1,
            pady=1
        )

        command_area = tk.Frame(
            console_panel,
            bg=PANEL,
            height=54
        )
        command_area.pack(fill="x", padx=10, pady=10)

        self.command_entry = tk.Entry(
            command_area,
            bg=INPUT_BACKGROUND,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Consolas", 11)
        )
        self.command_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=10,
            padx=(0, 8)
        )

        self.command_entry.insert(
            0,
            "Enter a server command..."
        )

        self.command_entry.bind(
            "<FocusIn>",
            self.clear_command_placeholder
        )

        self.command_entry.bind(
            "<Return>",
            lambda event: self.send_command()
        )

        send_button = self.create_button(
            command_area,
            "SEND",
            BLUE,
            BLUE_DARK,
            self.send_command,
            width=10
        )
        send_button.pack(side="right")

        self.update_buttons()

    def create_info_card(
        self,
        parent: tk.Widget,
        heading: str,
        value: str
    ) -> tk.Label:
        card = tk.Frame(
            parent,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        tk.Label(
            card,
            text=heading,
            bg=PANEL,
            fg=TEXT_MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=14, pady=(12, 2))

        value_label = tk.Label(
            card,
            text=value,
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 15, "bold")
        )
        value_label.pack(anchor="w", padx=14, pady=(0, 12))

        return value_label

    # =====================================================
    # SETTINGS PAGE
    # =====================================================

    def create_settings_page(self) -> None:
        canvas = tk.Canvas(
            self.settings_tab,
            bg=BACKGROUND,
            highlightthickness=0
        )
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            self.settings_tab,
            orient="vertical",
            command=canvas.yview
        )
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        settings_container = tk.Frame(
            canvas,
            bg=BACKGROUND
        )

        canvas_window = canvas.create_window(
            (0, 0),
            window=settings_container,
            anchor="nw"
        )

        settings_container.bind(
            "<Configure>",
            lambda event: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(
                canvas_window,
                width=event.width
            )
        )

        general_panel = self.create_settings_panel(
            settings_container,
            "GENERAL SERVER SETTINGS"
        )
        general_panel.pack(fill="x", pady=(10, 12))

        self.add_text_setting(
            general_panel,
            "Server Name / MOTD",
            "motd",
            "A Minecraft Server"
        )

        self.add_text_setting(
            general_panel,
            "Server Port",
            "server-port",
            "25565"
        )

        self.add_text_setting(
            general_panel,
            "Maximum Players",
            "max-players",
            "5"
        )

        self.add_dropdown_setting(
            general_panel,
            "Game Mode",
            "gamemode",
            {
                "Survival": "0",
                "Creative": "1",
                "Adventure": "2",
                "Spectator": "3"
            }
        )

        self.add_dropdown_setting(
            general_panel,
            "Difficulty",
            "difficulty",
            {
                "Peaceful": "0",
                "Easy": "1",
                "Normal": "2",
                "Hard": "3"
            }
        )

        gameplay_panel = self.create_settings_panel(
            settings_container,
            "GAMEPLAY"
        )
        gameplay_panel.pack(fill="x", pady=(0, 12))

        self.add_boolean_setting(
            gameplay_panel,
            "Player versus Player",
            "pvp",
            True
        )

        self.add_boolean_setting(
            gameplay_panel,
            "Spawn Monsters",
            "spawn-monsters",
            True
        )

        self.add_boolean_setting(
            gameplay_panel,
            "Spawn Animals",
            "spawn-animals",
            True
        )

        self.add_boolean_setting(
            gameplay_panel,
            "Allow Nether",
            "allow-nether",
            True
        )

        self.add_boolean_setting(
            gameplay_panel,
            "Command Blocks",
            "enable-command-block",
            False
        )

        self.add_boolean_setting(
            gameplay_panel,
            "Allow Flight",
            "allow-flight",
            False
        )

        network_panel = self.create_settings_panel(
            settings_container,
            "NETWORK AND SECURITY"
        )
        network_panel.pack(fill="x", pady=(0, 12))

        self.add_boolean_setting(
            network_panel,
            "Online Authentication",
            "online-mode",
            True
        )

        self.add_boolean_setting(
            network_panel,
            "Whitelist",
            "white-list",
            False
        )

        self.add_text_setting(
            network_panel,
            "View Distance",
            "view-distance",
            "10"
        )

        memory_panel = self.create_settings_panel(
            settings_container,
            "JAVA MEMORY"
        )
        memory_panel.pack(fill="x", pady=(0, 12))

        self.minimum_ram = tk.StringVar(value="2")
        self.maximum_ram = tk.StringVar(value="4")

        self.add_custom_dropdown(
            memory_panel,
            "Starting RAM",
            self.minimum_ram,
            ["1", "2", "3", "4", "6", "8"],
            "GB"
        )

        self.add_custom_dropdown(
            memory_panel,
            "Maximum RAM",
            self.maximum_ram,
            ["1", "2", "3", "4", "6", "8", "10", "12"],
            "GB"
        )

        actions = tk.Frame(
            settings_container,
            bg=BACKGROUND
        )
        actions.pack(fill="x", pady=(0, 20))

        reload_button = self.create_button(
            actions,
            "RELOAD SETTINGS",
            PANEL_LIGHT,
            BORDER,
            self.load_properties,
            width=18
        )
        reload_button.pack(side="left")

        save_button = self.create_button(
            actions,
            "SAVE SETTINGS",
            GREEN,
            GREEN_DARK,
            self.save_easy_settings,
            width=18
        )
        save_button.pack(side="right")

    def create_settings_panel(
        self,
        parent: tk.Widget,
        title: str
    ) -> tk.Frame:
        outer = tk.Frame(
            parent,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        tk.Label(
            outer,
            text=title,
            bg=PANEL_LIGHT,
            fg=TEXT,
            anchor="w",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=11
        ).pack(fill="x")

        content = tk.Frame(
            outer,
            bg=PANEL
        )
        content.pack(fill="x", padx=14, pady=8)

        return content

    def add_text_setting(
        self,
        parent: tk.Widget,
        label_text: str,
        property_name: str,
        default_value: str
    ) -> None:
        row = self.create_setting_row(parent, label_text)

        variable = tk.StringVar(value=default_value)
        self.property_entries[property_name] = variable

        entry = tk.Entry(
            row,
            textvariable=variable,
            bg=INPUT_BACKGROUND,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 10)
        )
        entry.pack(
            side="right",
            fill="x",
            expand=True,
            ipady=7
        )

    def add_boolean_setting(
        self,
        parent: tk.Widget,
        label_text: str,
        property_name: str,
        default_value: bool
    ) -> None:
        row = self.create_setting_row(parent, label_text)

        variable = tk.BooleanVar(value=default_value)
        self.property_entries[property_name] = variable

        checkbox = tk.Checkbutton(
            row,
            variable=variable,
            text="Enabled",
            bg=PANEL,
            fg=TEXT,
            activebackground=PANEL,
            activeforeground=TEXT,
            selectcolor=INPUT_BACKGROUND,
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        checkbox.pack(side="right")

    def add_dropdown_setting(
        self,
        parent: tk.Widget,
        label_text: str,
        property_name: str,
        choices: dict[str, str]
    ) -> None:
        row = self.create_setting_row(parent, label_text)

        display_variable = tk.StringVar(
            value=next(iter(choices.keys()))
        )

        self.property_entries[property_name] = display_variable

        combo = ttk.Combobox(
            row,
            textvariable=display_variable,
            values=list(choices.keys()),
            state="readonly",
            style="Server.TCombobox",
            width=24
        )
        combo.pack(side="right")

        display_variable.choice_map = choices

    def add_custom_dropdown(
        self,
        parent: tk.Widget,
        label_text: str,
        variable: tk.StringVar,
        values: list[str],
        suffix: str
    ) -> None:
        row = self.create_setting_row(parent, label_text)

        suffix_label = tk.Label(
            row,
            text=suffix,
            bg=PANEL,
            fg=TEXT_MUTED,
            font=("Segoe UI", 10)
        )
        suffix_label.pack(side="right", padx=(8, 0))

        combo = ttk.Combobox(
            row,
            textvariable=variable,
            values=values,
            state="readonly",
            style="Server.TCombobox",
            width=10
        )
        combo.pack(side="right")

    def create_setting_row(
        self,
        parent: tk.Widget,
        label_text: str
    ) -> tk.Frame:
        row = tk.Frame(
            parent,
            bg=PANEL
        )
        row.pack(fill="x", pady=7)

        tk.Label(
            row,
            text=label_text,
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 10),
            width=25,
            anchor="w"
        ).pack(side="left")

        return row

    # =====================================================
    # ADVANCED PAGE
    # =====================================================

    def create_advanced_page(self) -> None:
        panel = tk.Frame(
            self.advanced_tab,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        panel.pack(fill="both", expand=True, pady=10)

        header = tk.Frame(
            panel,
            bg=PANEL_LIGHT
        )
        header.pack(fill="x")

        tk.Label(
            header,
            text="RAW SERVER.PROPERTIES EDITOR",
            bg=PANEL_LIGHT,
            fg=TEXT,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=14, pady=12)

        self.properties_box = scrolledtext.ScrolledText(
            panel,
            bg=INPUT_BACKGROUND,
            fg="#d8e1e8",
            insertbackground=TEXT,
            selectbackground=BLUE_DARK,
            relief="flat",
            borderwidth=0,
            wrap=tk.NONE,
            font=("Consolas", 10),
            padx=12,
            pady=12
        )
        self.properties_box.pack(
            fill="both",
            expand=True,
            padx=1,
            pady=1
        )

        button_row = tk.Frame(
            panel,
            bg=PANEL,
            height=60
        )
        button_row.pack(fill="x", padx=12, pady=12)

        reload_button = self.create_button(
            button_row,
            "RELOAD FILE",
            PANEL_LIGHT,
            BORDER,
            self.load_properties,
            width=14
        )
        reload_button.pack(side="left")

        save_button = self.create_button(
            button_row,
            "SAVE FILE",
            GREEN,
            GREEN_DARK,
            self.save_raw_properties,
            width=14
        )
        save_button.pack(side="right")

    # =====================================================
    # BUTTON CREATION
    # =====================================================

    def create_button(
        self,
        parent: tk.Widget,
        text: str,
        normal_color: str,
        hover_color: str,
        command,
        width: int = 13
    ) -> tk.Button:
        button = tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            bg=normal_color,
            fg="#ffffff",
            activebackground=hover_color,
            activeforeground="#ffffff",
            disabledforeground="#77808a",
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=9
        )

        button.normal_color = normal_color
        button.hover_color = hover_color

        button.bind(
            "<Enter>",
            lambda event: self.button_hover_enter(button)
        )

        button.bind(
            "<Leave>",
            lambda event: self.button_hover_leave(button)
        )

        return button

    @staticmethod
    def button_hover_enter(button: tk.Button) -> None:
        if str(button["state"]) != "disabled":
            button.configure(bg=button.hover_color)

    @staticmethod
    def button_hover_leave(button: tk.Button) -> None:
        if str(button["state"]) != "disabled":
            button.configure(bg=button.normal_color)

    # =====================================================
    # SERVER CONTROL
    # =====================================================

    def start_server(self) -> None:
        if self.is_server_running():
            messagebox.showinfo(
                "Server Running",
                "The server is already running."
            )
            return

        if not os.path.isfile(JAR_FILE):
            messagebox.showerror(
                "Missing paper.jar",
                "paper.jar was not found.\n\n"
                "Place this program in the same folder as paper.jar."
            )
            return

        minimum_ram = self.minimum_ram.get()
        maximum_ram = self.maximum_ram.get()

        try:
            if int(minimum_ram) > int(maximum_ram):
                messagebox.showerror(
                    "Invalid RAM Settings",
                    "Starting RAM cannot be larger than maximum RAM."
                )
                return
        except ValueError:
            messagebox.showerror(
                "Invalid RAM Settings",
                "RAM settings must be numbers."
            )
            return

        self.clear_console()
        self.server_ready = False
        self.update_status("Starting...", YELLOW)
        self.add_console_text(
            "========================================\n"
            " Paper Server Studio\n"
            " Starting Minecraft server...\n"
            "========================================\n\n"
        )

        command = [
            "java",
            f"-Xms{minimum_ram}G",
            f"-Xmx{maximum_ram}G",
            "-jar",
            JAR_FILE
        ]

        try:
            creation_flags = 0

            if os.name == "nt":
                creation_flags = subprocess.CREATE_NO_WINDOW

            self.server_process = subprocess.Popen(
                command,
                cwd=BASE_FOLDER,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                creationflags=creation_flags
            )

            threading.Thread(
                target=self.read_server_output,
                daemon=True
            ).start()

            self.update_buttons()

        except FileNotFoundError:
            self.server_process = None
            self.update_status("Java Missing", RED)
            self.update_buttons()

            messagebox.showerror(
                "Java Not Found",
                "Java could not be found.\n\n"
                "Make sure Java 8 is installed and the command "
                "'java -version' works."
            )

        except Exception as error:
            self.server_process = None
            self.update_status("Start Failed", RED)
            self.update_buttons()

            messagebox.showerror(
                "Server Start Error",
                str(error)
            )

    def stop_server(self) -> None:
        if not self.is_server_running():
            messagebox.showinfo(
                "Server Offline",
                "The server is not currently running."
            )
            return

        self.update_status("Stopping...", YELLOW)
        self.send_server_text("stop")
        self.add_console_text("\n[Manager] Safely stopping server...\n")
        self.update_buttons()

    def restart_server(self) -> None:
        if not self.is_server_running():
            self.start_server()
            return

        confirmed = messagebox.askyesno(
            "Restart Server",
            "Restart the Minecraft server?\n\n"
            "The world will be saved before restarting."
        )

        if not confirmed:
            return

        threading.Thread(
            target=self.restart_worker,
            daemon=True
        ).start()

    def restart_worker(self) -> None:
        self.root.after(
            0,
            lambda: self.update_status("Restarting...", YELLOW)
        )

        self.send_server_text("stop")

        while self.is_server_running():
            time.sleep(0.25)

        time.sleep(1)

        self.root.after(0, self.start_server)

    def read_server_output(self) -> None:
        process = self.server_process

        if process is None or process.stdout is None:
            return

        try:
            for line in iter(process.stdout.readline, ""):
                if not line:
                    break

                self.add_console_text(line)
                self.inspect_server_line(line)

        except Exception as error:
            self.add_console_text(
                f"\n[Console reader error: {error}]\n"
            )

        process.wait()

        self.server_ready = False
        self.server_process = None

        self.root.after(
            0,
            lambda: self.update_status("Offline", RED)
        )

        self.root.after(0, self.update_buttons)
        self.add_console_text("\n[Server process ended]\n")

    def inspect_server_line(self, line: str) -> None:
        lower_line = line.lower()

        if "done (" in lower_line and "for help" in lower_line:
            self.server_ready = True
            self.root.after(
                0,
                lambda: self.update_status("Online", GREEN)
            )

        if "starting minecraft server on" in lower_line:
            self.root.after(0, self.refresh_info_cards)

        if "joined the game" in lower_line:
            self.root.after(0, self.request_player_list)

        if "left the game" in lower_line:
            self.root.after(0, self.request_player_list)

        if "players online:" in lower_line:
            self.parse_player_list(line)

        if "address already in use" in lower_line:
            self.root.after(
                0,
                lambda: self.update_status("Port In Use", RED)
            )

    def send_command(self) -> None:
        command = self.command_entry.get().strip()

        if not command or command == "Enter a server command...":
            return

        if not self.is_server_running():
            messagebox.showwarning(
                "Server Offline",
                "Start the server before sending commands."
            )
            return

        if command.startswith("/"):
            command = command[1:]

        self.send_server_text(command)
        self.add_console_text(f"> {command}\n")

        self.command_entry.delete(0, tk.END)

    def send_server_text(self, command: str) -> None:
        if not self.is_server_running():
            return

        try:
            if self.server_process and self.server_process.stdin:
                self.server_process.stdin.write(command + "\n")
                self.server_process.stdin.flush()

        except Exception as error:
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Command Error",
                    str(error)
                )
            )

    def request_player_list(self) -> None:
        if self.is_server_running():
            self.send_server_text("list")

    def parse_player_list(self, line: str) -> None:
        try:
            text = line.lower()

            if "there are" in text and "players online" in text:
                after_are = text.split("there are", 1)[1]
                count_text = after_are.split("of", 1)[0].strip()
                count = int(count_text)

                maximum = self.get_property_value(
                    "max-players",
                    "5"
                )

                self.root.after(
                    0,
                    lambda: self.players_card_value.configure(
                        text=f"{count} / {maximum}"
                    )
                )

        except Exception:
            pass

    def is_server_running(self) -> bool:
        return (
            self.server_process is not None
            and self.server_process.poll() is None
        )

    # =====================================================
    # PROPERTIES
    # =====================================================

    def read_property_dictionary(self) -> dict[str, str]:
        properties: dict[str, str] = {}

        if not os.path.isfile(PROPERTIES_FILE):
            return properties

        try:
            with open(
                PROPERTIES_FILE,
                "r",
                encoding="utf-8"
            ) as file:
                for raw_line in file:
                    line = raw_line.strip()

                    if not line or line.startswith("#"):
                        continue

                    if "=" not in line:
                        continue

                    key, value = line.split("=", 1)
                    properties[key.strip()] = value.strip()

        except Exception:
            pass

        return properties

    def load_properties(self) -> None:
        properties = self.read_property_dictionary()

        for property_name, variable in self.property_entries.items():
            if property_name not in properties:
                continue

            value = properties[property_name]

            if isinstance(variable, tk.BooleanVar):
                variable.set(value.lower() == "true")

            elif hasattr(variable, "choice_map"):
                choice_map = variable.choice_map
                display_name = next(
                    (
                        name
                        for name, stored_value in choice_map.items()
                        if stored_value == value
                    ),
                    next(iter(choice_map.keys()))
                )
                variable.set(display_name)

            else:
                variable.set(value)

        self.properties_box.delete("1.0", tk.END)

        if os.path.isfile(PROPERTIES_FILE):
            try:
                with open(
                    PROPERTIES_FILE,
                    "r",
                    encoding="utf-8"
                ) as file:
                    self.properties_box.insert(
                        tk.END,
                        file.read()
                    )

            except Exception as error:
                messagebox.showerror(
                    "Properties Error",
                    str(error)
                )

        else:
            self.properties_box.insert(
                tk.END,
                "# server.properties has not been generated.\n"
                "# Start the server once to create it.\n"
            )

        self.refresh_info_cards()

    def save_easy_settings(self) -> None:
        properties = self.read_property_dictionary()

        for property_name, variable in self.property_entries.items():
            if isinstance(variable, tk.BooleanVar):
                value = "true" if variable.get() else "false"

            elif hasattr(variable, "choice_map"):
                value = variable.choice_map.get(
                    variable.get(),
                    variable.get()
                )

            else:
                value = str(variable.get())

            properties[property_name] = value

        try:
            with open(
                PROPERTIES_FILE,
                "w",
                encoding="utf-8"
            ) as file:
                file.write("#Minecraft server properties\n")
                file.write("#Edited by Paper Server Studio\n")

                for key, value in properties.items():
                    file.write(f"{key}={value}\n")

            self.load_properties()

            messagebox.showinfo(
                "Settings Saved",
                "Server settings were saved!\n\n"
                "Restart the server for every change to apply."
            )

        except Exception as error:
            messagebox.showerror(
                "Save Error",
                str(error)
            )

    def save_raw_properties(self) -> None:
        contents = self.properties_box.get(
            "1.0",
            tk.END
        ).rstrip() + "\n"

        try:
            with open(
                PROPERTIES_FILE,
                "w",
                encoding="utf-8"
            ) as file:
                file.write(contents)

            self.load_properties()

            messagebox.showinfo(
                "File Saved",
                "server.properties was saved successfully."
            )

        except Exception as error:
            messagebox.showerror(
                "Save Error",
                str(error)
            )

    def get_property_value(
        self,
        key: str,
        fallback: str
    ) -> str:
        return self.read_property_dictionary().get(
            key,
            fallback
        )

    # =====================================================
    # DISPLAY HELPERS
    # =====================================================

    def update_status(
        self,
        status_text: str,
        color: str
    ) -> None:
        self.status_label.configure(text=status_text)
        self.status_dot.itemconfigure(
            self.status_circle,
            fill=color
        )

    def update_buttons(self) -> None:
        running = self.is_server_running()

        self.start_button.configure(
            state="disabled" if running else "normal",
            bg="#2a323c" if running else GREEN
        )

        self.stop_button.configure(
            state="normal" if running else "disabled",
            bg=RED if running else "#2a323c"
        )

        self.restart_button.configure(
            state="normal" if running else "disabled",
            bg=YELLOW if running else "#2a323c"
        )

    def refresh_file_status(self) -> None:
        if os.path.isfile(JAR_FILE):
            self.jar_card_value.configure(
                text="paper.jar ✓"
            )
        else:
            self.jar_card_value.configure(
                text="Missing!"
            )

    def refresh_info_cards(self) -> None:
        max_players = self.get_property_value(
            "max-players",
            "5"
        )

        port = self.get_property_value(
            "server-port",
            "25565"
        )

        self.players_card_value.configure(
            text=f"0 / {max_players}"
        )

        self.port_card_value.configure(
            text=port
        )

        self.ram_card_value.configure(
            text=f"{self.maximum_ram.get()} GB"
        )

        self.refresh_file_status()

    def clear_console(self) -> None:
        self.console_box.configure(state="normal")
        self.console_box.delete("1.0", tk.END)
        self.console_box.configure(state="disabled")

    def add_console_text(self, text: str) -> None:
        self.root.after(
            0,
            lambda: self.insert_console_text(text)
        )

    def insert_console_text(self, text: str) -> None:
        self.console_box.configure(state="normal")
        self.console_box.insert(tk.END, text)
        self.console_box.see(tk.END)
        self.console_box.configure(state="disabled")

    def clear_command_placeholder(self, event=None) -> None:
        if self.command_entry.get() == "Enter a server command...":
            self.command_entry.delete(0, tk.END)

    def open_server_folder(self) -> None:
        try:
            if os.name == "nt":
                os.startfile(BASE_FOLDER)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", BASE_FOLDER])
            else:
                subprocess.Popen(["xdg-open", BASE_FOLDER])

        except Exception as error:
            messagebox.showerror(
                "Folder Error",
                str(error)
            )

    # =====================================================
    # CLOSING
    # =====================================================

    def close_program(self) -> None:
        if self.is_server_running():
            answer = messagebox.askyesno(
                "Server Is Running",
                "The Minecraft server is still running.\n\n"
                "Stop it safely, save the world, and close?"
            )

            if not answer:
                return

            self.closing_program = True
            self.update_status("Stopping...", YELLOW)
            self.send_server_text("stop")

            threading.Thread(
                target=self.wait_then_close,
                daemon=True
            ).start()

            return

        self.root.destroy()

    def wait_then_close(self) -> None:
        timeout = 30
        started = time.time()

        while self.is_server_running():
            if time.time() - started > timeout:
                break

            time.sleep(0.25)

        self.root.after(0, self.root.destroy)


# =========================================================
# START PROGRAM
# =========================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = PaperServerManager(root)
    root.mainloop()