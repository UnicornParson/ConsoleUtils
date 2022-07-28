#include "dryengine.h"

#include <QObject>
#include <QDir>
#include <QFile>
#include <QFileInfo>

#include "archivereader.h"

DryEngine::DryEngine(QObject* parent):
    QObject(parent),
    m_fmt(Formats::invalid),
    m_noArch(false),
    m_noPrescan(false),
    filesCount(0)
{

}

bool DryEngine::exec(const QString& folder, bool abortOnFail)
{
    bool ret = false;
    do
    {
        if(folder.isEmpty() || !QDir(folder).exists())
        {
            qWarning() << "invalid folder" << folder;
        }

        // prescan stage

        if(!m_noPrescan)
        {
            qInfo() << "PRESCAN STAGE";
            auto processor = [this](const QString& path)->bool
            {
                return counterProcessor(path);
            };
            ret = runFolder(folder, processor, abortOnFail);
            if(!ret && abortOnFail)
            {
                qWarning() << "prescan failed";
                break;
            }
            qInfo() << "PRESCAN STAGE - done. count:" << filesCount;
        }



        qInfo() << "SCAN STAGE";
        // scan stage
        auto processor = [this](const QString& path)->bool
        {
            return readerProcessor(path);
        };
        ret = runFolder(folder, processor, abortOnFail);
    }
    while(false);
    return ret;
}

bool DryEngine::runFolder(const QString& folder, const fileProcessor& processor , bool abortOnFail)
{

    QDir f(folder);
    if(folder.isEmpty() || !f.exists())
    {
        qWarning() << "no folder";
        return false;
    }
    qInfo() << "process" << folder;
    f.setFilter(QDir::Dirs | QDir::Files | QDir::NoSymLinks | QDir::NoDot | QDir::NoDotDot);
    foreach (QFileInfo fileInfo, f.entryInfoList())
    {
        qInfo() << fileInfo;
        if(fileInfo.isFile())
        {
            bool processorResult = processor(fileInfo.absoluteFilePath());
            if(abortOnFail && !processorResult)
            {
                qWarning() << "fail on" << fileInfo.absoluteFilePath();
                return false;
            }
        }
        else if (fileInfo.isDir())
        {
            bool folderResult = runFolder(fileInfo.absoluteFilePath(), processor, abortOnFail);
            if(abortOnFail && !folderResult)
            {
                qWarning() << "fail on folder" << fileInfo.absoluteFilePath();
                return false;
            }
        }
    }
    return true;
}

bool DryEngine::runArchive(const QString& path, const fileProcessor& processor , bool abortOnFail)
{
    qWarning() << "ARCHIVE!" << path;
    return true;
}

bool DryEngine::listArchive(const QString& path)
{
    ArchiveReader reader(this);
    QStringList enties = reader.contentList(path);
    filesCount += enties.count();
    return true;
}

bool DryEngine::counterProcessor(const QString& path)
{
    qInfo() << "process" << path;
    QFileInfo info(path);
    bool ret = false;

    if(info.isFile())
    {
        ++filesCount;
        ret = true;
        if(ArchiveReader::isArchive(info.filePath()))
        {
            ret = listArchive(info.filePath());
        }
    }
    else if (info.isDir())
    {
        const auto processor = [this](const QString& path)->bool
        {
            return counterProcessor(path);
        };
        ret = runFolder(path, processor);
    }
    return ret;
}

bool DryEngine::readerProcessor(const QString& path)
{
    return true;
}
