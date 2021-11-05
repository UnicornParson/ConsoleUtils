#include <QApplication>
#include <QDebug>
#include "screenshot.h"

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    Screenshot engine;
    QString screenName;
    bool waitScreenName = false;
    QString fname;
    bool first = true;
    for(const QString& arg: a.arguments())
    {
        if(first)
        {
            first = false;
            continue;
        }
        if (arg == "-l")
        {
            waitScreenName = false;
            for(const QString& s: engine.screens())
            {
                qDebug() << s;
            }
            return 0;
        }
        else if(arg == "-s")
        {
            waitScreenName = true;
            continue;
        }
        else if(waitScreenName)
        {
            screenName = arg;
            waitScreenName = false;
        }
        else
        {
            fname = arg;
        }
    }
    QScreen* screen = engine.screen(screenName);
    if(screen == nullptr)
    {
        qFatal("invalid screen");
    }
    bool rc = engine.take(screen, fname);
    if(rc)
    {
        qDebug("done");
        return 0;
    }
    else
    {
        qFatal("failed");
    }

}
