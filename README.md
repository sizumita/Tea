# Tea Plugin System
Teaは、Asyncioのpluginシステムです。
設定したコネクタがeventをコールすることで、pluginの処理が呼び出されます。


# Example
```python
from tea import Tea

tea = Tea()
tea.register_connector("DiscordConnector")

tea.blend()

```

# Plugins
## Connectors
コネクタの一覧です。

## Plugins
プラグインの一覧です。