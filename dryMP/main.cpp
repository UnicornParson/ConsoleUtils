#include "dryengine.h"
#include "qsettings.h"
#include <QCoreApplication>
#include <QSettings>
#include <QTextCodec>
#include <QDateTime>
#include <QDebug>
#include <QDir>
#include <QFileInfo>
#include "utils.h"
#include "archivereader.h"

CONST_STRING LOGS_BASE_DIR("logs/");
CONST_STRING CONFIG_FILE("config.ini");
CONST_STRING CONFIG_GROUP("DRY");
CONST_STRING CONFIG_KEY_FMT(CONFIG_GROUP + "/fmt");
CONST_STRING CONFIG_KEY_NOARCH(CONFIG_GROUP + "/noarch");
CONST_STRING CONFIG_KEY_TMP(CONFIG_GROUP + "/tmp");
CONST_STRING CONFIG_KEY_TMP2(CONFIG_GROUP + "/tmp2");

int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);
    QTextCodec::setCodecForLocale(QTextCodec::codecForName("UTF-8"));
    QString path = QString(argv[0]);
    int lastSlash = path.lastIndexOf('\\');
    const QString binDir = path.left(lastSlash + 1);
    const QString logDir = Utils::pathNormalize(binDir + LOGS_BASE_DIR + QDateTime::currentDateTime().toString("dd.MM.yyyy_hh.mm.ss"));

    const QString configFile = Utils::pathNormalize(binDir + "/../../../" + CONFIG_FILE);
    qDebug() << configFile;
    QSettings settings(configFile,QSettings::Format::IniFormat);
    qDebug() << settings.status();

QString tmp = Utils::pathNormalize(binDir + "/tmp");
QString tmpCandidate = settings.value(CONFIG_KEY_TMP, QString()).toString().trimmed();
if(!tmpCandidate.isEmpty() && QDir(tmpCandidate).exists())
{
    tmp = tmpCandidate;
}
else
{
    tmpCandidate = settings.value(CONFIG_KEY_TMP2, QString()).toString().trimmed();
    if(!tmpCandidate.isEmpty() && QDir(tmpCandidate).exists())
    {
        tmp = tmpCandidate;
    }
}

QDir base("I:\\dl\\");


DryEngine engine;
engine.setFmt(DryEngine::Formats::html);
engine.setTmp(tmp);
engine.setNoPrescan(false);
engine.exec("I:\\dl\\", true);


    return a.exec();
}
