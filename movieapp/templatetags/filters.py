from django import template 
import locale
locale.setlocale(locale.LC_TIME, 'ru_RU')
register = template.Library() 


@register.filter
def cut(value:str): 
    return value[0:4]

@register.filter
def time(value:str): 
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
    year = value.split("-")[0]
    month = value.split("-")[1]
    day = value.split("-")[2]
    return f"{day}.{month}.{year}"

@register.filter
def nameline(value:str):
    return value.replace(" ", "\n")

@register.filter
def tohours(value:int):
    return value//60

@register.filter
def rating_color(value:int):
    if float(value)==0:
        return "secondary"
    if float(value)<=4:
        return "danger"
    if float(value)>=7:
        return "success"
    return "warning"