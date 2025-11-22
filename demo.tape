Output docs/demo.gif

Require uv

Set Shell "zsh"
Set Theme "OneHalfLight"
Set FontSize 12
Set Width 800
Set Height 450
Set Framerate 10

Env PS1 "user@demo:datatalk$ "

Type "uv run dtalk"
Sleep 500ms
Enter

Sleep 2s

Type "uv run dtalk sample_data/sales_data.csv"
Sleep 500ms
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
