Output docs/demo.gif

Require uv

Set Shell "zsh"
Set Theme "Builtin Light"
Set FontSize 18
Set Width 1000
Set Height 600
Set Framerate 60

Env PS1 "user@demo:datatalk$ "

Type "uv run dtalk sample_data/sales_data.csv --hide-suggestions"
Sleep 500ms
Enter

Sleep 5s

Type "show me total sales by region"
Sleep 4s
Enter

Sleep 10s

Type "what are the top 3 products by revenue?"
Sleep 4s
Enter

Sleep 10s

Ctrl+C
Sleep 500ms
