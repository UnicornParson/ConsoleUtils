#include "archivereader.h"
#include "qfileinfo.h"
#include "qnamespace.h"
#include "qprocess.h"
#include "qstringalgorithms.h"
#include <QProcess>
#include <QDebug>
#include <QFile>
#include <QRegularExpression>
#include <QFileInfo>

namespace
{
static const QRegularExpression archiveMasks("\\.7z$|\\.rar$|\\.zip$|\\.z$|\\.001$|\\.tar$|\\.xz$|\\.iso$|\\.gz$|\\.bz2$");
}

ArchiveReader::ArchiveReader(QObject *parent)
    : QObject{parent},
      m_7zapp("7z")
{

}

bool ArchiveReader::setApp(const QString& appname)
{
    QString lastApp = m_7zapp;
    m_7zapp = appname;
    bool ret = test();
    if(!ret)
    {
        m_7zapp = lastApp;
    }
    return ret;
}

bool ArchiveReader::test()
{
    AppRc rc = execApp("i", {});
    return (rc.first == 0);
}

ArchiveReader::AppRc ArchiveReader::execApp(const QString& c, const QStringList &arguments)
{
    QStringList fullArgsList = {c, "-sccUTF-8","-scsUTF-8", "-bt"};
    fullArgsList << arguments;

    QProcess p(this);
    p.start(m_7zapp, fullArgsList, QIODevice::ReadWrite|QIODevice::Unbuffered);
    if (!p.waitForStarted())
    {
        qWarning() << "cannot start " << m_7zapp;
        return ArchiveReader::AppRc(-1, {});
    }
    if (!p.waitForFinished())
    {
        qWarning() << "cannot finish " << m_7zapp;
        return ArchiveReader::AppRc(-1, {});
    }

    int rc = p.exitCode();
    const QString out = QString(p.readAllStandardOutput());
    const QString err = stringCleanup(QString(p.readAllStandardError()));

    const QStringList list = out.split(QRegularExpression("\r|\n"), Qt::SkipEmptyParts);
    if(rc != 0)
    {
        qWarning() << "app error:"  << err;
    }
    return ArchiveReader::AppRc(rc, list);
}

QString ArchiveReader::stringCleanup(const QString& s) const
{
    QString out = s;
    out = out.remove(QRegularExpression("\r|\n"));
    while(out.contains("  "))
    {
        out.replace("  ", " ");
    }
    return out;
}

QStringList ArchiveReader::contentList(const QString& path)
{
    if(path.trimmed().isEmpty())
    {
        qWarning() << "empty path";
        return QStringList();
    }

    if(!QFile::exists(path))
    {
        qWarning() << "no file in" << path;
        return QStringList();
    }
    AppRc rc = execApp("l", {path});

    if(rc.first != 0)
    {
        qWarning() << "invalid 7z exit code" << rc.first;
        for(const QString& line: rc.second)
        {
            qWarning() << QString("[%1:] %2").arg(m_7zapp, stringCleanup(line));
        }
        return QStringList();
    }

    const QStringList& list = rc.second;
    QString prev;
    int nameIndex = 0;
    bool headerLine = false;
    QStringList ret;
    for(const QString& line: list)
    {

        if(line.startsWith("-------"))
        {
            if(headerLine)
            {
                // footer. stop
                break;
            }
            headerLine = true;
            nameIndex = prev.indexOf("Name");
            if(nameIndex < 0)
            {
                qWarning() << "no name in header " << prev << nameIndex;
                break;
            }
            continue;
        }
        prev = line;
        if(!headerLine)
        {
            continue;
        }

        if(line.size() <= nameIndex)
        {
            qWarning() << "line " << line << "too short. need" << nameIndex + 1;
            continue;
        }
        QString fname = line.right(line.size() - nameIndex);
        ret << fname;
    }
    return ret;
}

bool ArchiveReader::extract(const QString& path, const QString& target)
{
    if(path.trimmed().isEmpty())
    {
        qWarning() << "empty path";
        return false;
    }

    if(!QFile::exists(path))
    {
        qWarning() << "no file in" << path;
        return false;
    }

    AppRc rc = execApp("x", {"-y", QString("-o%1").arg(target), path});

    if(rc.first != 0)
    {
        qWarning() << "invalid 7z exit code" << rc;
        return false;
    }

    const QStringList& list = rc.second;
    for(const QString& s: list)
    {
        qDebug() << QString("[%1:] %2").arg(m_7zapp, stringCleanup(s));
    }
    return (rc.first == 0);
}

bool ArchiveReader::isArchive(const QString& path)
{
    if(path.isEmpty() || !QFileInfo(path).isFile())
    {
        return false;
    }
    return archiveMasks.match(path.trimmed().toLower()).hasMatch();
}
