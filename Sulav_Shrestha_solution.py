"""
I have assumed best hr to be the one with least labour cost percentage and
worst hr to be the one with max labour cost and no sales
I have also considered hrs from 09:00 to 23:00(so upto hr starting 22:00) as that was the time in work shift
"""
#Importing necessary tools
from datetime import timedelta, datetime
import csv
from itertools import islice
#Defining fmt as format for 24hr time
fmt = "%H:%M"

def process_shifts(path_to_csv):
    #Defining dict as dictionary
    dict={}
    #Defing list to store values
    start_time=[]
    labour_cost=[]
    break_starts=[]
    break_end=[]
    shift_end=[]
    #Code to open and store csv file in lists
    with open(path_to_csv, mode='r') as inp:
        reader = csv.reader(inp)
        #Code starts from 2nd row to avoid copying the heading
        for rows in islice(reader, 1, None):
            shift_end.append(rows[1])
            start_time.append(rows[3])
            #Splitting the break time to get start time and end time in different list
            start_break, end_break = rows[0].split("-")
            break_starts.append(start_break)
            break_end.append(end_break)
            #Storing labour cost as a number
            labour_cost.append(float(rows[2]))
    # Removing PM and AM from from break start and end
    for bs in range(0, len(break_starts)):
        if "PM" in break_starts[bs].upper():
            break_starts[bs] = break_starts[bs].replace('PM', '')
        if "AM" in break_starts[bs].upper():
            break_starts[bs] = break_starts[bs].replace('AM', '')
        if "AM" in break_end[bs].upper():
            break_end[bs] = break_end[bs].replace('AM', '')
        if "PM" in break_end[bs].upper():
            break_end[bs] = break_end[bs].replace('PM', '')
            # Adding 12 to account for PM
            break_end[bs] = (float(break_end[bs])+12)
            break_starts[bs] = (float(break_starts[bs]) + 12)
        if float(break_starts[bs])< float(datetime.strptime(start_time[bs], fmt).strftime("%H")):
            #Adding 12 to make sense of the break time(can't have break without starting work)
            break_end[bs] = (float(break_end[bs]) + 12)
            break_starts[bs] = (float(break_starts[bs]) + 12)
        #Making everything string
        break_starts[bs] = str(float(break_starts[bs]))+"0"
        break_end[bs] = str(float(break_end[bs]))+"0"
        #Replacing . with :
        break_end[bs] = break_end[bs].replace(".", ":")
        break_starts[bs] = break_starts[bs].replace(".", ":")
        #Ensuring 24hr format
        break_end[bs] = datetime.strptime(break_end[bs],fmt).strftime("%H:%M")
        break_starts[bs] = datetime.strptime(break_starts[bs],fmt).strftime("%H:%M")
    #Treating end of break time as end of shift and break end time as start of a shift
    for add in range(0,len(shift_end)):
        start_time.append(break_end[add])
        labour_cost.append(labour_cost[add])
        break_starts.append(shift_end[add])
    #Looping over all the lists to find hrs and corresponding cost
    for s in range(0,len(start_time)):
        td=datetime.strptime(start_time[s],fmt)
        te=datetime.strptime(break_starts[s],fmt)
        # Ensuring 24hr format
        t = td.strftime("%H") + ":00"
        #Accounting for starting at differnt minute than 00
        if int(td.strftime("%M")) !=0:
            a = (-float(td.strftime("%M")) / 60) * labour_cost[s]
            if t in dict:
                mm= a + dict[t]
            else:
                mm=a
            dict.update({t:mm})

        while td < te:
            #Ensuring 24hr format
            t = td.strftime("%H")+":00"
            a = labour_cost[s]
            #Cumulating labour cost
            if t in dict:
                a += dict[t]
            dict.update({t: a})
            td += timedelta(minutes=60)
        #Accounting for shift ending other than 00 minute
        if int(te.strftime("%M"))!= 0:
            tt = te.strftime("%H") + ":00"
            a = (-1+int(te.strftime("%M"))/60)*labour_cost[s]
            if tt in dict:
                a += dict[tt]
            dict.update({tt: a})
    return dict

def process_sales(path_to_csv):
    #Defining dic as dictionary
    dic={'09:00': 0,
          '10:00': 0,
          '11:00': 0,
          '12:00': 0,
          '13:00': 0,
          '14:00': 0,
          '15:00': 0,
          '16:00': 0,
          '17:00': 0,
          '18:00': 0,
          '19:00': 0,
          '20:00': 0,
          '21:00': 0,
          '22:00': 0}
    #Reading transaction file
    with open(path_to_csv, mode='r') as inp:
        reader = csv.reader(inp)
        #Ignoring row with heading
        for rows in islice(reader, 1, None):
            time=datetime.strptime(rows[1], fmt)
            #Getting rid of minute
            tii= time.strftime("%H")+":00"
            sss=float(rows[0])
            #Cumulating sales in that hour
            if tii in dic:
                sss+=dic[tii]
            dic.update({tii:sss})
    return dic

def compute_percentage(shifts, sales):
    #Defining dictionary
    pdict = {}
    for tim in sales:
        cost = shifts[tim]
        sale = sales[tim]
        #Storing -cost when sale is Null
        if sale==0:
            pe = -cost
        #Storing labour cost percentage per sale
        else:
            pe = cost/sale*100
        pdict.update({tim : pe})
    return pdict

def best_and_worst_hour(percentages):
    #Naming best and worst as first hour the shift starts
    best=list(percentages.keys())[0]
    worst=list(percentages.keys())[0]
    for bw in percentages:
        # When we have no sales in the hour we are comparing to(i.e value stored is -cost)
        if percentages[bw]<=0:
            #Comparing values with best and if the latter one is better storing it as best
            if percentages[bw]>percentages[best]:
                best=bw
            #Comparing values with worst and if the latter one is worse storing it as worst
            if percentages[bw]<percentages[worst]:
                worst=bw
        #When the value we are comparing to has sale(i.e value stored is labour cost percentage)
        else:
            if percentages[best]>0:
                # Comparing values with best and if the latter one is better storing it as best
                if percentages[bw]<percentages[best]:
                    best=bw
            else:
                best=bw

            if percentages[worst] > 0:
                # Comparing values with worst and if the latter one is worse storing it as worst
                if percentages[bw] > percentages[worst]:
                    worst=bw
    return [best,worst]

def main(path_to_shifts, path_to_sales):

    shifts_processed = process_shifts(path_to_shifts)
    sales_processed = process_sales(path_to_sales)
    percentages = compute_percentage(shifts_processed, sales_processed)
    best_hour, worst_hour = best_and_worst_hour(percentages)
    return best_hour, worst_hour

if __name__ == '__main__':
    # You can change this to test your code, it will not be used
    path_to_sales = "transactions.csv"
    path_to_shifts = "work_shifts.csv"
    best_hour, worst_hour = main(path_to_shifts, path_to_sales)
shifts = process_shifts(path_to_shifts)
sales= process_sales(path_to_sales)
ss={}
print(best_hour,worst_hour)
print(compute_percentage(shifts, sales))
for key in sorted(shifts):
    ss.update({key:shifts[key]})
print(ss)
print(sales)

