import flet as ft
import asyncio
import random


def main(page: ft.Page):
    page.title = "Blinking Color Card"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    
    # Available colors (red, yellow, blue)
    COLORS = [ft.Colors.RED, ft.Colors.YELLOW, ft.Colors.BLUE]
    
    # Create a card with blinking animation - fills window height
    card = ft.Container(
        width=320,
        expand=True,  # Fill available vertical space
        bgcolor=ft.Colors.RED,
        border_radius=15,
        alignment=ft.Alignment.CENTER,
        shadow=ft.BoxShadow(
            spread_radius=2,
            blur_radius=25,
            color=ft.Colors.RED_900,
            offset=ft.Offset(0, 6),
        ),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(
                    icon=ft.Icons.COLOR_LENS,
                    size=40,
                    color=ft.Colors.WHITE,
                ),
                ft.Text(
                    "COLOR BLINKER",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
            ],
        ),
        animate_opacity=ft.Animation(duration=250, curve=ft.AnimationCurve.EASE_IN_OUT),
        animate_scale=ft.Animation(duration=150, curve=ft.AnimationCurve.BOUNCE_OUT),
    )
    
    # State variables
    is_blinking = False
    blink_task = None
    last_color = ft.Colors.RED  # Track last color to avoid repeats
    
    # Language state
    current_language = "en"  # "en" or "es"
    
    # Language strings
    lang_strings = {
        "en": {
            "title": "Blink Settings",
            "interval": "Blink Interval (seconds):",
            "speed": "Animation Speed:",
            "language": "Display Language:",
            "english": "English",
            "spanish": "Spanish",
            "cancel": "Cancel",
            "start": "Start",
            "card_title": "COLOR BLINKER",
            "fab_tooltip": "Click to start/stop",
        },
        "es": {
            "title": "Configuración de Parpadeo",
            "interval": "Intervalo de Parpadeo (segundos):",
            "speed": "Velocidad de Animación:",
            "language": "Idioma de Pantalla:",
            "english": "Inglés",
            "spanish": "Español",
            "cancel": "Cancelar",
            "start": "Comenzar",
            "card_title": "PARPADEADOR DE COLORES",
            "fab_tooltip": "Clic para iniciar/detener",
        }
    }
    
    def get_text(key):
        """Get text for current language"""
        return lang_strings[current_language][key]
    
    def update_language():
        """Update all displayed text to current language"""
        nonlocal settings_dialog
        
        # Update dialog
        settings_dialog.title = ft.Text(get_text("title"), size=20)
        
        # Update content (recreate with new language)
        settings_dialog.content = ft.Column(
            width=300,
            controls=[
                ft.Text(get_text("interval"), size=14),
                interval_slider,
                ft.Text(get_text("speed"), size=14),
                speed_slider,
                ft.Text(get_text("language"), size=14),
                ft.RadioGroup(
                    content=ft.Column([
                        ft.Radio(value="en", label=get_text("english")),
                        ft.Radio(value="es", label=get_text("spanish")),
                    ]),
                    value=current_language,
                    on_change=on_language_change,
                ),
            ],
        )
        
        # Update actions
        settings_dialog.actions = [
            ft.TextButton(get_text("cancel"), on_click=lambda e: page.pop_dialog()),
            ft.TextButton(get_text("start"), on_click=start_blinking),
        ]
        
        # Update card title
        card.content.controls[1] = ft.Text(
            get_text("card_title"),
            size=20,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
        )
        
        # Update FAB tooltip
        fab.tooltip = get_text("fab_tooltip")
        
        page.update()
    
    def on_language_change(e):
        """Handle language selection change"""
        nonlocal current_language
        current_language = e.control.value
        update_language()
    
    # Slider components for AlertDialog
    interval_slider = ft.Slider(
        min=0.1,
        max=5.0,
        value=2.0,
        divisions=49,
        label="Interval: {value}s",
        width=250,
        round=1,  # Show 1 decimal place
    )
    
    speed_slider = ft.Slider(
        min=0.5,
        max=5.0,
        value=1.0,
        divisions=45,
        label="Speed: {value}x",
        width=250,
        round=1,  # Show 1 decimal place
    )
    
    def start_blinking(e):
        """Start blinking with slider values"""
        nonlocal is_blinking, blink_task
        
        # Close the dialog
        page.pop_dialog()
        
        # Start blinking immediately
        is_blinking = True
        card.scale = 1.1
        fab.visible = False  # Hide FAB when blinking
        
        # Create and start the blinking task
        blink_task = asyncio.create_task(blink_card())
        
        card.update()
        fab.update()
    
    def get_random_color():
        """Get a random color that's different from the last one"""
        available_colors = [c for c in COLORS if c != last_color]
        new_color = random.choice(available_colors)
        return new_color
    
    async def blink_card():
        """Blink the card with random colors, keeping each color for multiple blinks"""
        nonlocal last_color
        color_change_counter = 0
        current_color = last_color
        
        while is_blinking:
            # Get current values from sliders (reads fresh each cycle)
            speed = speed_slider.value if speed_slider.value > 0 else 1.0
            interval = interval_slider.value if interval_slider.value >= 0.1 else 0.1
            
            # Fade out (speed adjusted - higher speed = faster)
            fade_time = 0.25 / speed
            card.opacity = 0.1  # More dramatic fade (was 0.3)
            card.scale = 0.95  # Slight shrink
            card.update()
            await asyncio.sleep(fade_time)
            
            # Change color every 3 blinks, otherwise keep same color
            if color_change_counter >= 3:
                current_color = get_random_color()
                last_color = current_color
                card.bgcolor = current_color
                color_change_counter = 0
            else:
                # Keep current color
                card.bgcolor = current_color
                color_change_counter += 1
            
            # Fade in (speed adjusted - higher speed = faster)
            card.opacity = 1.0
            card.scale = 1.0  # Full size
            card.update()
            await asyncio.sleep(fade_time)
            
            # Wait for user-specified interval (speed adjusted - higher speed = faster)
            await asyncio.sleep(interval / speed)
    
    def stop_blinking(e):
        """Stop blinking"""
        nonlocal is_blinking, blink_task
        
        is_blinking = False
        card.scale = 1.0
        card.opacity = 1.0
        card.bgcolor = ft.Colors.RED  # Reset to initial color
        last_color = ft.Colors.RED
        
        # Cancel the blinking task
        if blink_task:
            blink_task.cancel()
        
        # Update FAB
        fab.icon = ft.Icons.FAVORITE
        fab.bgcolor = ft.Colors.BLUE_700
        fab.foreground_color = ft.Colors.RED
        fab.visible = True
        
        card.update()
        fab.update()
    
    # Create the AlertDialog
    settings_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(get_text("title"), size=20),
        content=ft.Column(
            width=300,
            controls=[
                ft.Text(get_text("interval"), size=14),
                interval_slider,
                ft.Text(get_text("speed"), size=14),
                speed_slider,
                ft.Text(get_text("language"), size=14),
                ft.RadioGroup(
                    content=ft.Column([
                        ft.Radio(value="en", label=get_text("english")),
                        ft.Radio(value="es", label=get_text("spanish")),
                    ]),
                    value=current_language,
                    on_change=on_language_change,
                ),
            ],
        ),
        actions=[
            ft.TextButton(get_text("cancel"), on_click=lambda e: page.pop_dialog()),
            ft.TextButton(get_text("start"), on_click=start_blinking),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def on_fab_click(e):
        """Handle FAB click - either start or stop"""
        if is_blinking:
            stop_blinking(e)
        else:
            # Show dialog to get settings first
            page.show_dialog(settings_dialog)
    
    def on_card_click(e):
        """Handle card click - start or stop blinking immediately"""
        nonlocal is_blinking, blink_task
        
        if is_blinking:
            # If already blinking, stop it
            is_blinking = False
            card.scale = 1.0
            card.opacity = 1.0
            card.bgcolor = ft.Colors.RED  # Reset to initial color
            last_color = ft.Colors.RED
            
            # Cancel the blinking task
            if blink_task:
                blink_task.cancel()
            
            # Show FAB again
            fab.icon = ft.Icons.FAVORITE
            fab.bgcolor = ft.Colors.BLUE_700
            fab.foreground_color = ft.Colors.RED
            fab.visible = True
            
            card.update()
            fab.update()
        else:
            # Start blinking immediately with current slider values
            is_blinking = True
            card.scale = 1.1
            fab.visible = False  # Hide FAB when blinking
            
            # Create and start the blinking task
            blink_task = asyncio.create_task(blink_card())
            
            card.update()
            fab.update()
    
    def on_hover(e):
        """Scale card on hover"""
        if e.data == "true":
            card.scale = 1.05
        else:
            card.scale = 1.0 if not is_blinking else 1.1
        card.update()
    
    # Create Floating Action Button (initially visible)
    fab = ft.FloatingActionButton(
        icon=ft.Icons.FAVORITE,
        bgcolor=ft.Colors.BLUE_700,
        foreground_color=ft.Colors.RED,
        elevation=8,
        on_click=on_fab_click,
        tooltip=get_text("fab_tooltip"),
    )
    
    # Add handlers
    card.on_click = on_card_click
    card.on_hover = on_hover
    
    # Set the floating action button
    page.floating_action_button = fab
    
    # Add the card with expand to fill height
    display_card=ft.SafeArea(content=card, expand=True)
    page.add(display_card)


if __name__ == "__main__":
    ft.run(main)