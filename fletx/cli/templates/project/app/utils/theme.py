import flet as ft

#### APP LIGHT THEME
light_theme = ft.Theme(
    color_scheme=ft.ColorScheme(
        primary="#4F46E5",        # Indigo 600 (accent color)
        primary_container="#EEF2FF",  # Light indigo background
        secondary="#64748B",      # Slate 500
        secondary_container="#F1F5F9",  # Light slate background
        surface="#FFFFFF",
        background="#F9FAFB",
        error="#DC2626",          # Red 600
        on_primary="#FFFFFF",
        on_secondary="#FFFFFF",
        on_surface="#1F2937",     # Gray 800 (text on white)
        on_background="#1F2937",
        on_error="#FFFFFF"
    ),
    use_material3=True,
    scaffold_bgcolor = "#F9FAFB",
    visual_density=ft.VisualDensity.COMFORTABLE,
    font_family="Roboto"
)


#### APP DARK THEME
dark_theme = ft.Theme(
    color_scheme=ft.ColorScheme(
        primary="#4F46E5",        # Indigo 500
        primary_container = "#FCECD5",  # Indigo background
        secondary="#94A3B8",      # Slate 400
        secondary_container="#253745",  # Dark slate background
        surface="#16191C",        # Gray 900
        background="#191918",     # Gray 950
        error="#F87171",          # Red 400
        on_primary="#FFFFFF",
        on_secondary="#000000",
        on_surface="#E5E7EB",     # Gray 200
        on_background="#E5E7EB",
        on_error="#000000"
    ),
    # brightness=ft.Brightness.DARK,
    scaffold_bgcolor = "#0F1319",
    use_material3=True,
    visual_density=ft.VisualDensity.COMFORTABLE,
    font_family="Roboto"
)