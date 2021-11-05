#ifndef SCREENSHOT_H
#define SCREENSHOT_H

#include <QWidget>

class Screenshot : public QWidget
{
    Q_OBJECT
public:
    explicit Screenshot(QWidget *parent = nullptr);
    bool take(QScreen* s, const QString& outPath);
    QStringList screens();
    QScreen* screen(const QString& name);
protected:
    QString cleanName(const QString& name);

};

#endif // SCREENSHOT_H
