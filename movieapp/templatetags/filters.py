from django import template 
import locale
locale.setlocale(locale.LC_TIME, 'ru_RU')
register = template.Library() 


@register.filter
def cut(value:str): 
    return value[0:4]

@register.filter
def time(value:int): 
    value = int(value)
    days = value//60//24
    hours = value//60%24
    minutes = value%60
    return f"{ str(days) +" д. " if days> 0  else ""}{ str(hours) +" ч. " if hours> 0  else ""}{str(minutes) + " мин."} "

@register.filter
def roundrating(value): 
    return round(value, 2)

import calendar
@register.filter
def month(value:str): 
    return f"{calendar.month_name[int(value.split(".")[0])]} {value.split(".")[1]}"

@register.filter
def format_date(value:str):
    value = value.split("-")
    year = value[0]
    month = value[1]
    day = value[2]
    return f"{day}.{month}.{year}"

@register.filter
def year(value:str):
    return value.split("-")[0]

@register.filter
def m_type(value:bool):
    return "tv" if value else "movie"

@register.filter
def link(value:str):
    return value.replace(" ", "%20")

@register.filter
def tohours(value):
    return int(value)//60

@register.filter
def rating_color(value:int):
    if float(value)==0:
        return "secondary"
    if float(value)<=4:
        return "danger"
    if float(value)>=7:
        return "success"
    return "warning"

@register.filter
def genres_count(value:str):
    return len(set(value.split(',')))-1


@register.filter
def incline(value, arg):
    return arg+str(value)