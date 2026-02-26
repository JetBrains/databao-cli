from databao_context_engine import DatabaoContextPluginLoader


def main() -> None:
    plugin_ids = DatabaoContextPluginLoader().get_loaded_plugin_ids()
    print(repr(plugin_ids))


if __name__ == "__main__":
    main()
