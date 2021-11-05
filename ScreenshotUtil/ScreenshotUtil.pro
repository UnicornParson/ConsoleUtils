QT += core gui widgets

CONFIG += c++17 console


# The following define makes your compiler emit warnings if you use
# any Qt feature that has been marked deprecated (the exact warnings
# depend on your compiler). Please consult the documentation of the
# deprecated API in order to know how to port your code away from it.
DEFINES += QT_DEPRECATED_WARNINGS

# You can also make your code fail to compile if it uses deprecated APIs.
# In order to do so, uncomment the following line.
# You can also select to disable deprecated APIs only up to a certain version of Qt.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

SOURCES += \
        main.cpp \
        screenshot.cpp

INCLUDE_PATH += $$PWD

CONFIG(debug, debug|release) {
  DESTDIR = bin/debug
  OBJECTS_DIR = bin/debug/.obj
  MOC_DIR = bin/debug/.moc
  RCC_DIR = bin/debug/.rcc
  UI_DIR = bin/debug/.ui
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

target.files += dlls/*.dll
target.path += $$DESTDIR
INSTALLS += target

HEADERS += \
    screenshot.h
