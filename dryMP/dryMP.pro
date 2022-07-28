QT -= gui
QT += core core5compat
CONFIG += c++17 console
CONFIG -= app_bundle

QMAKE_CXXFLAGS_WARN_ON -= -Wreorder -Wformat= -WsignConversion

SOURCES += \
        archivereader.cpp \
        dryengine.cpp \
        main.cpp \
        utils.cpp

CONFIG(debug, debug|release) {
  DESTDIR = bin/debug
  OBJECTS_DIR = bin/debug/.obj
  MOC_DIR = bin/debug/.moc
  RCC_DIR = bin/debug/.rcc
  UI_DIR = bin/debug/.ui

  CONFIG += TOOLLIB_BADWAY_TRAP
}

CONFIG(release, debug|release) {
  # enable optimisation
  QMAKE_CXXFLAGS_RELEASE += -O4
  QMAKE_CXXFLAGS_RELEASE -= -O2
  QMAKE_CXXFLAGS_RELEASE -= -O3
  QMAKE_CXXFLAGS_RELEASE -= -Os
  QMAKE_CXXFLAGS += -O4
  QMAKE_CXXFLAGS -= -O2
  QMAKE_CXXFLAGS -= -O3
  QMAKE_CXXFLAGS -= -Os

  DESTDIR = bin/release
  OBJECTS_DIR = bin/release/.obj
  MOC_DIR = bin/release/.moc
  RCC_DIR = bin/release/.rcc
  UI_DIR = bin/release/.ui
}

HEADERS += \
    archivereader.h \
    dryengine.h \
    utils.h
