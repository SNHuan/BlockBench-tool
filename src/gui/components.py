import customtkinter as ctk

class InputField:
    def __init__(self, parent, label_text, default_value="", **kwargs):
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.label = ctk.CTkLabel(
            self.frame,
            text=label_text,
            font=ctk.CTkFont(size=14),
            width=120
        )
        self.entry = ctk.CTkEntry(
            self.frame,
            font=ctk.CTkFont(size=14),
            placeholder_text=default_value,
            **kwargs
        )
        
        self.label.pack(side="left", padx=5)
        self.entry.pack(side="left", padx=5, fill="x", expand=True)
