#include "utils.h"
#include <QDebug>

namespace
{
const QChar pathSeparator('/');
const QChar invalidPathSeparator('\\');
CONST_STRING doubleSeparator("//");
constexpr int WHILE_ITERATION_LIMIT(1024);
const QString SIZE_NAMES[] = {"B", "KB", "MB", "GB", "TB", "PB", "EB"};
}

Utils::Utils()
{

}

QString Utils::pathNormalize(const QString &in)
{
    uint iteration = 0;
    QString normalized = QString(in).replace(invalidPathSeparator, pathSeparator);
    while(normalized.contains(doubleSeparator))
    {
        ++iteration;
        if (iteration > WHILE_ITERATION_LIMIT)
        {
            qWarning() << QString("potential incorrent while. iteration %1, string %2").arg(iteration).arg(normalized);
        }
        normalized.replace(doubleSeparator, pathSeparator);
    }
    return normalized;
}
