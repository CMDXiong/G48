# -*- mode: python -*-

block_cipher = None


a = Analysis(['manage.spec'],
             pathex=['E:\\G48\\G48'],
             binaries=[],
             datas=[(r'E:\G48\G48\front\static_root',r'.\front\static_root'), (r'E:\G48\G48\front\templates', r'.\front\templates')],
             hiddenimports=['django.template.context_processors','django.contrib.auth.context_processors','django.contrib.messages.context_processors',
			 'django.template.loaders.filesystem', 'multiprocessing', 'apps.home.urls','apps.home.websocket','django.contrib.messages.middleware', 'django.contrib.admin.apps',
			 'django.contrib.auth.apps','django.contrib.contenttypes.apps','django.contrib.sessions.apps',
			 'django.contrib.messages.apps', 'django.contrib.staticfiles.apps',
			 'django.contrib.auth.middleware', 'django.contrib.sessions.middleware',
			 'django.contrib.sessions.serializers', 'loaders.filesystem'
			 ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='manage',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
