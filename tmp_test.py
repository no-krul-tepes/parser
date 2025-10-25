from schedule_parser.parser import parse_schedule_html

HTML = """

<HTML>
<HEAD>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=windows-1251">
<META NAME="Generator" CONTENT="Microsoft Word 97">
<TITLE>106</TITLE>
<META NAME="Template" CONTENT="C:\PROGRAM FILES\MICROSOFT OFFICE\OFFICE\html.dot">
</HEAD>
<BODY>
<SCRIPT>var d=new Date(Date.parse(document.lastModified)); var m=''+(d.getMonth() + 1); if(m<10){m='0'+m;} var day=''+d.getDate(); if(day<10){day='0'+day;} var y=d.getFullYear(); var x=day+'.'+m+'.'+y; document.writeln("<P>Расписание обновлено "+x+"</P>");</SCRIPT>
<FONT FACE="Times New Roman" SIZE=5 COLOR="#0000ff"><P>Расписание занятий учебной группы:</FONT><FONT FACE="Times New Roman" SIZE=6 COLOR="#ff00ff"> 1123</P></FONT>
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
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">лек.ЭД 3 Оценка профессиональных рисков  ПЛИШКИНА О.В.  а.8240 эбж   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">пр.Гидромеханика КОТОВА Т.И.  а.8111а   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">ЭК по ФКС 4 ФКС 8  а.9-Спорт4   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">лек.Экология ЖАРНИКОВА Е.В.  а.8241 экол   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">лаб.Гидромеханика БАДМАЕВА Т.Ц.  а.8111а   </FONT></TD>
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
<B><I><FONT FACE="Arial" SIZE=2><P ALIGN="CENTER">Срд</B></I></FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">лек.Экология ЖАРНИКОВА Е.В.  а.8241 экол   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">лек.Гидрогеология ПЛЮСНИН А.М.  а.8228 и/д   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">пр.Гидрогеология ПЛЮСНИН А.М.  а.8127   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">пр.Гидрогеология ПЛЮСНИН А.М.  а.8127   </FONT></TD>
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
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">пр.Механика 2 БЫКОВ А.В.  а.722   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">лек.Механика 2 БЫКОВ А.В.  а.722   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">пр.Экология ЖАРНИКОВА Е.В.  а.8241 экол   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">лек.Гидромеханика КОТОВА Т.И.  а.8111а   </FONT></TD>
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
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">пр.Военная кафедра- 1 п/г ВК 5  а.15-098   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">ЭК по ФКС 4 ФКС 8  а.9-Спорт4   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">пр.Военная кафедра- 1 п/г ВК 5  а.15-098   </FONT></TD>
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
<B><I><FONT FACE="Arial" SIZE=2><P ALIGN="CENTER">Сбт</B></I></FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">лек.Сопротивление материалов АНЧИЛОЕВ Н.Н.  а.606   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1><P ALIGN="CENTER">лаб.Сопротивление материалов АНЧИЛОЕВ Н.Н.  а.606   </FONT></TD>
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
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> лек.Экология ЖАРНИКОВА Е.В.  а.8241 экол   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> пр.Экология ЖАРНИКОВА Е.В.  а.8241 экол   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> ЭК по ФКС 4 ФКС 8  а.9-Спорт4   </FONT></TD>
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
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
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
<B><I><FONT FACE="Arial" SIZE=2 COLOR="#0000ff"><P ALIGN="CENTER">Срд</B></I></FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> лек.ЭД 3 Оценка профессиональных рисков  ПЛИШКИНА О.В.  а.8240 эбж   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> пр.ЭД 3 Оценка профессиональных рисков  ПЛИШКИНА О.В.  а.8240 эбж   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> пр.Гидромеханика КОТОВА Т.И.  а.8111а   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> лек.Гидрогеология ПЛЮСНИН А.М.  а.8230   </FONT></TD>
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
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> пр.Экология ЖАРНИКОВА Е.В.  а.8241 экол   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> пр.ЭД 3 Оценка профессиональных рисков  ПЛИШКИНА О.В.  а.8240 эбж   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> лаб.Механика 2 БЫКОВ А.В.  а.720   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> пр.Механика 2 БЫКОВ А.В.  а.726-2 ТМиОК   </FONT></TD>
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
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> пр.Военная кафедра- 1 п/г ВК 5  а.15-098   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> ЭК по ФКС 4 ФКС 8  а.9-Спорт4   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> пр.Военная кафедра- 1 п/г ВК 5  а.15-098   </FONT></TD>
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
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> лек.Сопротивление материалов АНЧИЛОЕВ Н.Н.  а.606   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> пр.Сопротивление материалов АНЧИЛОЕВ Н.Н.  а.606   </FONT></TD>
<TD WIDTH="11%" VALIGN="TOP" HEIGHT=28>
<FONT FACE="Arial" SIZE=1 COLOR="#0000ff"><P ALIGN="CENTER"> _     </FONT></TD>
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
