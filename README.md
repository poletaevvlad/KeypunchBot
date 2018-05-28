# KeypunchBot

A TelegramBot that generates images of punched cards or punched tape with text
defined by user encoded. It can be accessed via the following link: 
[t.me/keypunch_bot](https://t.me/keypunch_bot).

KeypunchBot supports multiple encodings listed below. To see all characters 
supported by currently selected encoding use `/characters` command.

| Encoding name   | Command to activate | Storage medium         |
|-----------------|---------------------|------------------------|
| ASCII           | `/ascii`            | 80-column punched card |
| EBCDIC          | `/ebcdic`           | 80-column punched card |
| EBCDIC-880      | `/ebcdic880`        | 80-column punched card |
| ITA-2 (CCITT-2) | `/ita2`             | 5-bit punched tape     | 
| MTK-2           | `/mtk2`             | 5-bit punched tape     | 

KeypunchBot can generate images and send them as a photo or a document as PNG
or JPEG files. It can also generate text files. To see the list of all 
supported commands send `\help` command.

## Generated output examples

### Punched card (EBCDIC encoding)
![Pucnged card](sample_punched_card.png)

### Punched tape (ITA-2 encoding)
![Pucnged tape](sample_punched_tape.png)

## Dependencies

The KeypunchBot uses the following open-source libraries:

* [PyYAML](https://github.com/yaml)
* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
* [Pillow](http://python-pillow.org/)
* [gunicorn](https://http://gunicorn.org/)
* [pymongo](https://api.mongodb.com/python/current/)

File `keypunch_bot/images/encoded_symbols.png` is generated using by 
[png-font-generator](https://github.com/poletaevvlad/png-font-generator), 
which was written for the development of KeypunchBot.