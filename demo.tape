Output docs/demo.gif

Require uv

Set Shell "bash"
Set FontSize 32
Set Width 1920
Set Height 1080
Set Theme "Dracula"
Set Framerate 10

Env PS1 "user@demo:datatalk$ "

Type "uv run dtalk sample_data/sales_data.csv"
Sleep 100ms
Enter

Sleep 3s

Type "show me total sales by region"
Sleep 2s
Enter

Sleep 4s

Type "what are the top 3 products by revenue?"
Sleep 2s
Enter

Sleep 4s

Type "show me sales by product and region"
Sleep 2s
Enter

Sleep 4s

Ctrl+C
Sleep 500ms
