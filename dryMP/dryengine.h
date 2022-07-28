#ifndef DRYENGINE_H
#define DRYENGINE_H
#include <QObject>
#include <functional>

#include "qglobal.h"
#include "utils.h"

class DryEngine: public QObject
{
    Q_OBJECT
public:
    enum class Formats
    {
        json,
        out,
        html,
        sqlite,
        invalid
    };
    Q_ENUM(Formats)
    using fileProcessor = std::function<bool(const QString&)>;
    explicit DryEngine(QObject* parent = nullptr);
    bool exec(const QString& folder, bool abortOnFail = false);

    void setTmp(const QString& tmp){m_tmp = tmp;}
    void setFmt(DryEngine::Formats fmt){m_fmt = fmt;}
    void setNoArch(bool v){m_noArch = v;}
    void setNoPrescan(bool v){m_noPrescan = v;}
protected:

    bool runFolder(const QString& folder, const fileProcessor& processor , bool abortOnFail = false);
    bool runArchive(const QString& path, const fileProcessor& processor , bool abortOnFail = false);
    bool listArchive(const QString& path);
    bool counterProcessor(const QString& path);
    bool readerProcessor(const QString& path);


    QString m_tmp;
    Formats m_fmt;
    bool m_noArch;
    bool m_noPrescan;
    quint64 filesCount;
};

#endif // DRYENGINE_H
