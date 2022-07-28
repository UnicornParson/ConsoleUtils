#ifndef ARCHIVEREADER_H
#define ARCHIVEREADER_H

#include <QObject>

class ArchiveReader : public QObject
{
    Q_OBJECT
public:
    using AppRc = QPair<int, QStringList>;
    explicit ArchiveReader(QObject *parent = nullptr);
    bool setApp(const QString& appname);
    bool test();
    QStringList contentList(const QString& path);
    bool extract(const QString& path, const QString& target);
    static bool isArchive(const QString& path);
signals:
protected:
    QString stringCleanup(const QString& s) const;
    AppRc execApp(const QString& c, const QStringList &arguments = {});
    QString m_7zapp;

};

#endif // ARCHIVEREADER_H
