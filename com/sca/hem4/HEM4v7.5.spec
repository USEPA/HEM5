# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['multiwindow.py'],
<<<<<<< HEAD
             pathex=['C:\\Users\\David Lindsey\\OneDrive - SC&A, Inc\\HEM4Python\\Version_Master\\hem4\\com\\sca\\hem4'],
=======
             pathex=['C:\\Users\\David Lindsey\\OneDrive - SC&A, Inc\\HEM4Python\\version7\\hem4\\com\\sca\\hem4'],
>>>>>>> bd0859b6a8f371dbb8872f9d2b3014fbf2a1c141
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='HEM4v7.5',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='HEM4v7.5')
