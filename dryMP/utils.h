#ifndef UTILS_H
#define UTILS_H
#include <QString>

#define CONST_STRING static const QString

class Utils
{
public:
    Utils();
    static QString pathNormalize(const QString& in);
};

#endif // UTILS_H
