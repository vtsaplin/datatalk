Output docs/demo.gif

Require uv

Set Shell "zsh"
Set Theme "OneHalfLight"
Set FontSize 18
Set Width 1000
Set Height 600
Set Framerate 60

Env PS1 "user@demo:datatalk$ "

Type "uv run dtalk"
Sleep 500ms
Enter

Sleep 2s

Type "uv run dtalk sample_data/sales_data.csv --hide-suggestions"
Sleep 500ms
Enter

Sleep 3s

Type "show me total sales by region"
Sleep 2s
Enter

Sleep 5s

Type "n"
Sleep 500ms
Enter

Type "what are the top 3 products by revenue?"
Sleep 2s
Enter

Sleep 5s

Type "n"
Sleep 500ms
Enter

Type "show me sales by product and region"
Sleep 2s
Enter

Sleep 2s

Type "y"
Sleep 500ms
Enter

Sleep 5s

Ctrl+C
Sleep 500ms
