from rich.console import Console
from rich.panel import Panel
from rich.text import Text
console = Console()

panel = Text("Hello")
panel.on(click = "")
console.print(panel)
