# -*- mode: python ; coding: utf-8 -*-
# ─────────────────────────────────────────────────────────────
# ETL_Dashboard.spec
# Generato per MyWay Tools — ETL Dashboard
# Posiziona questo file nella stessa cartella di menu.py
# ─────────────────────────────────────────────────────────────

a = Analysis(
    ['menu.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('logo.ico', '.'),   # icona inclusa nell'exe
    ],
    hiddenimports=[

        # ── PANDAS ────────────────────────────────────────────
        'pandas',
        'pandas._libs',
        'pandas._libs.tslibs',
        'pandas._libs.tslibs.timedeltas',
        'pandas._libs.tslibs.np_datetime',
        'pandas._libs.tslibs.nattype',
        'pandas._libs.tslibs.offsets',
        'pandas._libs.tslibs.timestamps',
        'pandas._libs.tslibs.parsing',
        'pandas._libs.tslibs.period',
        'pandas._libs.tslibs.frequencies',
        'pandas._libs.skiplist',
        'pandas._libs.hashtable',
        'pandas._libs.index',
        'pandas._libs.lib',
        'pandas._libs.missing',
        'pandas._libs.ops',
        'pandas._libs.properties',
        'pandas._libs.reshape',
        'pandas._libs.writers',
        'pandas.core.arrays.integer',
        'pandas.core.arrays.floating',
        'pandas.core.arrays.boolean',
        'pandas.core.arrays.string_',
        'pandas.io.formats.style',

        # ── NUMPY ─────────────────────────────────────────────
        'numpy',
        'numpy.core._multiarray_umath',
        'numpy.core._multiarray_tests',
        'numpy.core.multiarray',
        'numpy.core.umath',
        'numpy.random',
        'numpy.linalg',

        # ── OPENPYXL ──────────────────────────────────────────
        'openpyxl',
        'openpyxl.styles',
        'openpyxl.styles.fonts',
        'openpyxl.styles.fills',
        'openpyxl.styles.borders',
        'openpyxl.styles.alignment',
        'openpyxl.styles.numbers',
        'openpyxl.styles.protection',
        'openpyxl.utils',
        'openpyxl.utils.dataframe',
        'openpyxl.utils.datetime',
        'openpyxl.chart',
        'openpyxl.drawing',
        'openpyxl.worksheet',
        'openpyxl.worksheet.table',
        'openpyxl.worksheet.filters',
        'openpyxl.worksheet.datavalidation',

        # ── PYARROW ───────────────────────────────────────────
        'pyarrow',
        'pyarrow.pandas_compat',
        'pyarrow.lib',
        'pyarrow.parquet',

        # ── XLRD ──────────────────────────────────────────────
        'xlrd',
        'xlrd.biffh',
        'xlrd.book',
        'xlrd.compdoc',
        'xlrd.formula',
        'xlrd.sheet',

        # ── XLWINGS ───────────────────────────────────────────
        'xlwings',
        'xlwings.main',
        'xlwings.utils',

        # ── COLORAMA ──────────────────────────────────────────
        'colorama',
        'colorama.ansi',
        'colorama.ansitowin32',
        'colorama.initialise',
        'colorama.winterm',

        # ── TQDM ──────────────────────────────────────────────
        'tqdm',
        'tqdm.auto',
        'tqdm.std',
        'tqdm.utils',

        # ── PSUTIL ────────────────────────────────────────────
        'psutil',
        'psutil._pswindows',
        'psutil._psutil_windows',

        # ── PYSIDE6 ───────────────────────────────────────────
        'PySide6',
        'PySide6.QtWidgets',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtNetwork',

        # ── STDLIB usati dagli script ─────────────────────────
        'importlib',
        'importlib.util',
        'importlib.machinery',
        'contextlib',
        'threading',
        'logging',
        'logging.handlers',
        'shutil',
        'pathlib',
        'datetime',
        'copy',
        'time',
        're',
        'os',
        'sys',

    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Escludi roba inutile per ridurre dimensioni exe
        'tkinter',
        'matplotlib',
        'scipy',
        'PIL',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'setuptools',
        'distutils',
        'unittest',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],                    # ← era a.binaries, togli
    name='MyWay Tools',
    debug=False,
    strip=False,
    upx=False,             # ← metti False
    console=False,
    icon='logo.ico',
)

coll = COLLECT(
    exe,
    a.binaries,            # ← aggiungi questo blocco
    a.datas,
    strip=False,
    upx=False,
    name='MyWay Tools'
)