import os

runtime_path = r'C:\TEMP\_runtime'
site_packages = os.path.join(runtime_path, 'Lib', 'site-packages')

# Menu.spec
block_cipher = None

a = Analysis(
    ['menu.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('version.txt', '.'),       # include la versione
        ('logo.ico', '.'),
    ],
    hiddenimports=[
        'xlwings',
        'xlrd',
        'openpyxl',  
        'pandas', 
        'win32com',
        'win32com.client',
        'pythoncom',
        'pywintypes',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,          # ← IMPORTANTE: modalità --onedir
    name='MyWayTools',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                  # False = nessuna finestra terminale
    icon='logo.ico',                # se hai il logo in formato .ico
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MyWayTools',              # ← nome cartella in dist/
)

pathex=[
    os.path.dirname(os.path.abspath(SPEC)),
    runtime_path,
    site_packages,
],