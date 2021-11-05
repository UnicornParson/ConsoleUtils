#include "screenshot.h"
#include <QScreen>
#include <QGuiApplication>
#include <QDebug>

Screenshot::Screenshot(QWidget *parent) : QWidget(parent)
{

}

QStringList Screenshot::screens()
{
    QStringList ret;
    QList<QScreen *> slist = QGuiApplication::screens();
    for(QScreen * s: slist)
    {
        if(s == nullptr)
        {
            continue;
        }
        ret.append(s->name());
    }
    return ret;
}

QString Screenshot::cleanName(const QString& name)
{
    QString s = name;
    s.remove('\\');
    return s;
}

QScreen* Screenshot::screen(const QString& name)
{
    QList<QScreen *> slist = QGuiApplication::screens();
    for(QScreen * s: slist)
    {

        if(s == nullptr)
        {
            continue;
        }
        QString sn = cleanName(s->name());
        if(sn == cleanName(name))
        {
            return s;
        }
    }
    return nullptr;
}

bool Screenshot::take(QScreen* s,const QString& outPath)
{
    bool bRet = false;
    do
    {
        if(outPath.isEmpty())
        {
            qWarning("empty out path");
            break;
        }
        if(s ==  nullptr)
        {
            s = QGuiApplication::primaryScreen();
        }
        if (!s)
        {
            qWarning("invalid screen");
            break;
        }

        QPixmap p = s->grabWindow(0);
        if (!p.save(outPath)) {
            qWarning("cannot save file");
            break;
        }
        bRet = true;
    }
    while(false);
    return bRet;
}
