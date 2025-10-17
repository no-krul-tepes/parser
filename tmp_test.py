import sys
from importlib import import_module
from pathlib import Path
from dataclasses import asdict

if __package__ is None or __package__ == "":
    package_dir = Path(__file__).resolve().parent
    parent_dir = package_dir.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))

    package_name = package_dir.name
    parser_module = import_module(f"{package_name}.parser")
    parse_schedule_html = parser_module.parse_schedule_html

HTML = """

<HTML>
<HEAD>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=windows-1251">
<META NAME="Generator" CONTENT="Microsoft Word 97">
<TITLE>4</TITLE>
<META NAME="Template" CONTENT="C:\PROGRAM FILES\MICROSOFT OFFICE\OFFICE\html.dot">
</HEAD>
<BODY>
<SCRIPT>var d=new Date(Date.parse(document.lastModified)); var m=''+(d.getMonth() + 1); if(m<10){m='0'+m;} var day=''+d.getDate(); if(day<10){day='0'+day;} var y=d.getFullYear(); var x=day+'.'+m+'.'+y; document.writeln("<P>Расписание обновлено "+x+"</P>");</SCRIPT>
<FONT FACE="Times New Roman" SIZE=5 COLOR="#0000ff"><P>Расписание занятий учебной группы:</FONT><FONT FACE="Times New Roman" SIZE=6 COLOR="#ff00ff"> К45/2</P></FONT>
<TABLE BORDER CELLSPACING=3 BORDERCOLOR="#000000" CELLPADDING=2 WIDTH=801>
<TR><TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<P ALIGN="CENTER"><FONT FACE="Arial">Пары</FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial"><P ALIGN="CENTER">1-я</FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial"><P ALIGN="CENTER">2-я</FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial"><P ALIGN="CENTER">3-я</FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial"><P ALIGN="CENTER">4-я</FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial"><P ALIGN="CENTER">5-я</FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial"><P ALIGN="CENTER">6-я</FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial"><P ALIGN="CENTER"></FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial"><P ALIGN="CENTER"></FONT></TD>
</TR>
<TR><TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial"><P ALIGN="CENTER">Время</FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<P ALIGN="CENTER">09:00-10:35 </TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<P ALIGN="CENTER">10:45-12:20 </TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<P ALIGN="CENTER">13:00-14:35 </TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<P ALIGN="CENTER">14:45-16:20 </TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<P ALIGN="CENTER">16:25-18:00 </TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<P ALIGN="CENTER">18:05-19:40 </TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<P ALIGN="CENTER"></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<P ALIGN="CENTER"></TD>
</TR>
<TR><TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<B><I><FONT FACE="Arial" SIZE=2><P ALIGN="CENTER">Пнд</B></I></FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">пр.История МИХЕЕВ Б.В.  а.0426   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">Физическая культура и спорт ФКС 21  а.9-Спорт1   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">лек.История МИХЕЕВ Б.В.  а.0310   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">пр.Обществознание ВАСИЛЬЕВ С.В.  а.707   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">_     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">_     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">    </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">    </FONT></TD>
</TR>
<TR><TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<B><I><FONT FACE="Arial" SIZE=2><P ALIGN="CENTER">Втр</B></I></FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">_     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">лек.География ФЕДОРОВА И.Э.  а.0100   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">пр.Математика ГЕРГЕНОВА Н.Д.  а.0310   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">пр.Химия СЯЧИНОВА Н.В.  а.8401   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">_     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">_     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">    </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">    </FONT></TD>
</TR>
<TR><TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<B><I><FONT FACE="Arial" SIZE=2><P ALIGN="CENTER">Срд</B></I></FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">пр.Русский язык АНГАРХАЕВА Ю.П.  а.0426   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">лек.Обществознание ВАСИЛЬЕВ С.В.  а.0339   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">пр.Родная литература МОЛОНОВА Л.Б.  а.0327   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">пр.География ФЕДОРОВА И.Э.  а.723   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">_     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">_     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">    </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">    </FONT></TD>
</TR>
<TR><TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<B><I><FONT FACE="Arial" SIZE=2><P ALIGN="CENTER">Чтв</B></I></FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">_     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">лек.Родная литература МОЛОНОВА Л.Б.  а.15-466   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">пр.Биология ИВАНЧИКОВ Е.А.  а.15-343   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">лаб.Информатика- 1 п/г ПАВЛОВА И.А.  а.15-357-2   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">_     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">_     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">    </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">    </FONT></TD>
</TR>
<TR><TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<B><I><FONT FACE="Arial" SIZE=2><P ALIGN="CENTER">Птн</B></I></FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">пр.Математика ГЕРГЕНОВА Н.Д.  а.0310   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">лек.Математика ГЕРГЕНОВА Н.Д.  а.0410   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">пр.Основы безопасности и защиты Родины ШАНТАГАРОВА Н.В.  а.8236 и/дэкол   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">пр.Иностранный язык ДАНЗАНОВА С.В.  а.0107   БАЗАРОВА М.Д. - а.718а</FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">_     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">_     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">    </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">    </FONT></TD>
</TR>
<TR><TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<B><I><FONT FACE="Arial" SIZE=2><P ALIGN="CENTER">Сбт</B></I></FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">_     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">_     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">_     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">_     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">_     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">_     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">    </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">    </FONT></TD>
</TR>
<TR><TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<B><I><FONT FACE="Arial" SIZE=2 COLOR="#0000ff"><P ALIGN="CENTER">Пнд</B></I></FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> пр.Литература МОЛОНОВА Л.Б.  а.8401   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> Физическая культура и спорт ФКС 21  а.9-Спорт1   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> лек.Химия СЯЧИНОВА Н.В.  а.8402   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER">     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER">     </FONT></TD>
</TR>
<TR><TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<B><I><FONT FACE="Arial" SIZE=2 COLOR="#0000ff"><P ALIGN="CENTER">Втр</B></I></FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> лек.Основы безопасности и защиты Родины ШАНТАГАРОВА Н.В.  а.8236 и/дэкол   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> лек.Математика ГЕРГЕНОВА Н.Д.  а.8433   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> пр.Математика ГЕРГЕНОВА Н.Д.  а.8401   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER">     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER">     </FONT></TD>
</TR>
<TR><TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<B><I><FONT FACE="Arial" SIZE=2 COLOR="#0000ff"><P ALIGN="CENTER">Срд</B></I></FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> пр.Физика ВАГАНОВА В.Г.  а.0410   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> лек.Русский язык АНГАРХАЕВА Ю.П.  а.8403   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> пр.Иностранный язык ДАНЗАНОВА С.В.  а.719   БАЗАРОВА М.Д. - а.0300</FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> лек.Физика ВАГАНОВА В.Г.  а.0316и/д   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER">     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER">     </FONT></TD>
</TR>
<TR><TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<B><I><FONT FACE="Arial" SIZE=2 COLOR="#0000ff"><P ALIGN="CENTER">Чтв</B></I></FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> пр.Обществознание ВАСИЛЬЕВ С.В.  а.0425и/д   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> лек.Биология ИВАНЧИКОВ Е.А.  а.0310   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> лек.Литература МОЛОНОВА Л.Б.  а.0310   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER">     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER">     </FONT></TD>
</TR>
<TR><TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<B><I><FONT FACE="Arial" SIZE=2 COLOR="#0000ff"><P ALIGN="CENTER">Птн</B></I></FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> лек.Обществознание ВАСИЛЬЕВ С.В.  а.0302и/д   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> лаб.Основы проект. деят-ти АНГАРХАЕВА Ю.П.  а.0107   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER">     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER">     </FONT></TD>
</TR>
<TR><TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<B><I><FONT FACE="Arial" SIZE=2 COLOR="#0000ff"><P ALIGN="CENTER">Сбт</B></I></FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> лаб.Информатика- 2 п/г ПАВЛОВА И.А.  а.728-3   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> лек.Информатика ПАВЛОВА И.А.  а.701   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER">     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER">     </FONT></TD>
</TR>
</TABLE>

</BODY>
</HTML>
"""

even, odd = parse_schedule_html(HTML, group_id=1)


def lesson_to_record(lesson):
    return {
        "group_id": lesson.group_id,
        "name": lesson.name,
        "lesson_date": lesson.lesson_date.isoformat(),
        "day_of_week": lesson.day_of_week,
        "lesson_number": lesson.lesson_number,
        "start_time": lesson.start_time.isoformat(timespec="minutes"),
        "end_time": lesson.end_time.isoformat(timespec="minutes"),
        "teacher_name": lesson.teacher_name,
        "cabinet_number": lesson.cabinet_number,
        "week_type": lesson.week_type.value,
        "raw_text": lesson.raw_text,
    }


def dump_records(title, lessons):
    print(f"\n{title}: {len(lessons)} записей")
    for record in sorted((lesson_to_record(lesson) for lesson in lessons),
                         key=lambda item: (item["week_type"], item["day_of_week"], item["lesson_number"])):
        print(record)


dump_records("Четная неделя", even)
dump_records("Нечетная неделя", odd)
