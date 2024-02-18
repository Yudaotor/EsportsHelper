# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py',
    'EsportsHelper\\Logger.py',
    'EsportsHelper\\Config.py',
    'EsportsHelper\\LoginHandler.py',
    'EsportsHelper\\Match.py',
    'EsportsHelper\\Twitch.py',
    'EsportsHelper\\VersionManager.py',
    'EsportsHelper\\Webdriver.py',
    'EsportsHelper\\YouTube.py',
    'EsportsHelper\\Utils.py',
    'EsportsHelper\\Rewards.py',
    'EsportsHelper\\I18n.py',
    'EsportsHelper\\League.py',
    'EsportsHelper\\Stats.py',
    'EsportsHelper\\Stream.py',
    'EsportsHelper\\GUIThread.py',
    'EsportsHelper\\LiveDataProvider.py',
    'EsportsHelper\\Drop.py',
    'EsportsHelper\\NetworkHandler.py',
    ],
    pathex=['C:\\Users\\Khalil\\Desktop\\EsportsHelper'],
    binaries=[],
    datas=[],
    hiddenimports=['selenium','rich','time','pathlib','logging','argparse','plyer.platforms.win.notification','cloudscraper'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['numpy','scipy','pandas','pytest','jieba','matplotlib','sklearn','html5lib','lxml','PyQt5.QtWebKit','PyQt5.QtXml','PyQt5.QtScript','tkinter','flask_socketio'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EsportsHelperV2.4.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='C:\\Users\\Khalil\\Desktop\\pyin\\EsportsHelper.ico'
)