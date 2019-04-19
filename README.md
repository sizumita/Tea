# Tea Plugin System β
Teaは、Asyncioのpluginシステムです。
設定したコネクタがeventをコールすることで、pluginの処理が呼び出されます。


# Example
## メインスクリプト

```python
# pluginsフォルダをメインスクリプトと同じ階層に作成してください。
from tea import Tea

tea = Tea()
tea.register_connector("DiscordConnector")

tea.blend()

```

## Plugin Example
作りたいプラグインのメインPythonスクリプト名
```python
# まず、pluginsフォルダに作成したいプラグインのファイルを作成してください。
# 次に、そのフォルダの中にconfig.ymlを作成してください。そして下に書いてあるコードを書いてください。
# そのあとconfig.ymlと同じ階層にこのスクリプトを書いてください。
from tea import Plugin

plugin = Plugin()


@plugin.event()
async def on_ready():
    # DiscordConnectorのon_ready eventをキャッチします。
    print("ready!")


def setup():
    return plugin


```

config.yml
```yaml
name: "プラグインの名前"
setup: "作りたいプラグインのメインPythonスクリプト名"
```

# Plugins
## Connectors
コネクタの一覧です。

## Plugins
プラグインの一覧です。