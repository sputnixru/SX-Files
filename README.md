### Получение файлов, передаваемых с кубсатов (для радиолюбителей)

Описание наземной части и python скрипта для сборки файлов

Набор инструментов:

1. SDR# + Soundmodem или GnuRadio with sputnix receive flowgraph
2. Soundmodem
3. Houston Telemetry Viewer v217.rc1
4. Python3
5. Git bash/anaconda prompt/powershell

Подробно приём телеметрии с кубсатов описан в [этой статье](http://viewnok.sputnix.ru/doku.php?id=lesson08_1). При настройке приёма необходимо ориентироваться на эту статью. Сбор файлов сводится к получению сообщений в Telemetry Viewer, получении лога с принятыми сообщениями, и его обработке скриптом.

Для Telemetry Viewer необходимо увеличение объема хранимых сообщений. Это изменяется во вкладке File->Parameters->HistoryDepth >= 20000.

Во время сеанса должны быть приняты сообщения 0xC20, 0xC2B (заголовочные) и 0xC24 - блоки данных. Файл допускается к сборке только если приняты все блоки данных для этого файла. Скрипт подскажет, если какие-либо блоки данных отсутствуют. Если такой же файл будет передаваться на следующем сеансе, то его можно будет 'дособрать'.

После окончания сеанса необходимо сохранить полученный лог в папку со скриптом. В Houston Telemetry Viewer: File->Save Log as.

Далее необходимо в любой командной строке (Git bash/ananconda prompt/cmd/powershell) перейти в папку со скриптом и запустить его, передав первым аргументом название обрабатываемого лога `python3 process_log_to_file.py LogNameWithFile.csv`. Принципиально важно, чтобы командная строка при обработке была открыта в папке со скриптом, посколько в этой директории будет создана папка tmp_files, в которой находятся карты получаемых файлов для "досборки", если он не был полностью принят на одном сеансе и передается повторно на другом.

Скрипт проинформирует, если какие-то блоки были не приняты. По умолчанию собранный файл будет собран только в случае, если были приняты все фрагменты. Однако есть возможность запустить скрипт с опцией `--force-dump`, при этом все фрагменты будут записаны последовательно, игнорируя отсутствующие. Целостность файла при этом нарушается и корректное открытие содержимого не обеспечивается, однако для ряда файлов это возможно. Команда запуска будет выглядеть следующим образом: `python3 process_log_to_file.py --force-dump LogNameWithFile.csv`

### File receiving from Cubesats (for radio amateurs)

Ground software & processing description

Toolkit:

1. SDR# + Soundmodem or GnuRadio with sputnix receive flowgraph
2. Soundmodem
3. Houston Telemetry Viewer v217.rc1
4. Python3
5. Git bash/anaconda prompt/powershell

Description of telemetry receiving from cubesats could be found by [link](http://viewnok.sputnix.ru/doku.php?id=en:lesson08_1), which describes basic setup. File receiving corresponds to decode messages in Telemetry Viewer, get logs and process it with script.

Increase message count in Telemerty viewer. Change this by clicking File->Parameters->HistoryDepth >= 20000.

Messages 0xC20, 0xC2B (headers) & 0xC24 (file fragments) must be received during the session. File will be dumped only if all fragments of the file has been received. Script will warn you if it find lost fragments. If same file is repeated on another session it is possible to сontinue collecting.

At the end of session save log in script location folder. In Telemetry Viewer click File->Save Log as.

Launch `python3 process_log_to_file.py LogNameWithFile.csv` in shell. Script will create `tmp_files` folder with temporary "map" files needed to store metadata and file fragments. 

Script will print warning if some fragments were not received . Specifing option `--force-dump` causes script to dump file ignoring lost fragments. Data integrity in this case is not guaranteed, so use it only if you really need. Launch like`python3 process_log_to_file.py --force-dump LogNameWithFile.csv`.