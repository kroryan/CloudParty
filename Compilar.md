 Cómo Compilar

  Windows (.exe)

  build_windows.bat
  Salida: dist\CloudParty.exe

  Linux (WSL2)

  Primero instala las dependencias del sistema:
  sudo apt update
  sudo apt install -y python3 python3-pip libappindicator3-1 gir1.2-appindicator3-0.1 python3-gi

  Luego compila:
  chmod +x build_linux.sh
  ./build_linux.sh
  Salida: dist/cloudparty

  Opcional: Crear AppImage

  chmod +x scripts/make_appimage.sh
  ./scripts/make_appimage.sh
  Salida: dist/CloudParty-1.20.1-x86_64.AppImage