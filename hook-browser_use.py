from PyInstaller.utils.hooks import collect_data_files

# Collect all templates, prompts, and other resource files
datas = collect_data_files("browser_use", include_py_files=True)


# Grab all files from browser_use/agent/prompts
datas += collect_data_files("browser_use.agent", includes=["prompts/*"])
datas += collect_data_files("browser_use.agent", includes=["*.md"])
# If there are JSON or txt resources in browser_use/
datas += collect_data_files("browser_use", includes=["*.json", "*.txt"])