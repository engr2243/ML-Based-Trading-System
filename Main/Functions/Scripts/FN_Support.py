### Relevant Libries
################################################
import pandas as pd
from datetime import datetime, time, date, timedelta
from dateutil.relativedelta import relativedelta
import calendar
import time as t
import os
import traceback
import inspect
import shutil
import glob

### Set Current Working Directory
################################################
WD = os.getcwd().split('Main')[0] + 'Main/'


# =======================================================================
class Drct:

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def csv_from(FILENAME,PRINT=False,LM=True):

        try:
            data = pd.read_csv(FILENAME,header=0,index_col=0,low_memory=LM)
            print(f"Imported: {FILENAME}") if PRINT else None
        except:
            try:
                ZIP_FN = FILENAME + '.gz'
                data = pd.read_csv(ZIP_FN,compression='gzip',header=0,index_col=0,low_memory=LM)
                
                print(f"Imported ZIP: {ZIP_FN}") if PRINT else None
            except:
                print(f"\nCSV Import Failed: {FILENAME}\n") if PRINT else None
                data = pd.DataFrame()
        return data
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def csv_to(data,FILENAME,LOG=False,ZIP=False,APPEND=False,IF_DIFFERENT=False,IF_DIFF_COLS=[],IF_DIFF_EXCLUDE=None,PRINT=False):

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>
        def run_log():

            ### Create Log Data
            #################################
            TODAY = datetime.now().strftime('%Y-%m-%d')
            log_timestamp = datetime.now().strftime('%Y-%m-%d %X')
            log_folder = str(FILENAME).split(str(FILENAME).split('/')[-1])[0][:-1].replace(WD,'')
            log_file = str(FILENAME).split('/')[-1].split('.')[0]
            log_path = FILENAME.replace(WD,'')

            LOG_FOLDER = f"{WD}Sources/csv_logs/{TODAY}/Pending"
            LOG_FILE = f"{LOG_FOLDER}/{datetime.now().strftime('%Y-%m-%d %H_%M_%S')} - {log_file}.csv"
            if not os.path.exists(LOG_FOLDER):
                Drct.create_folder(LOG_FOLDER)

            raw = {
            'timestamp': [log_timestamp],
            'folder': [log_folder],
            'file': [log_file],
            'path': [log_path],
            }
            log = pd.DataFrame(data=raw)

            print(f"{datetime.now():%I:%M:%S} | CSV Log | {log_path}")
            
            ### Export Log
            #################################
            try:
                log.to_csv(LOG_FILE)
            except Exception as e:
                ERROR_NAME = e
                ERROR_DETAILS = traceback.format_exc()
                ERROR_FUNCTION = inspect.stack()[0][3]+'()'
                print(f"\n\n{'*'*100}\nERROR at {ERROR_FUNCTION}\n{'*'*100}\n\n{ERROR_NAME}\n\n{ERROR_DETAILS}\n{'*'*100}\n{'*'*100}\n\n")
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>
        def export(data,FILENAME):
            if ZIP:
                if str(FILENAME).split('.')[-1] != 'gz':
                    if os.path.exists(FILENAME):
                        try:
                            os.remove(FILENAME)
                        except:
                            pass
                    FILENAME = FILENAME + '.gz'
                data.to_csv(FILENAME,compression='gzip')
            else:
                if os.path.exists(f"{FILENAME}.gz"):
                    try:
                        os.remove(f"{FILENAME}.gz")
                    except:
                        pass
                data.to_csv(FILENAME)
                
            print(f"Exported: {FILENAME}") if PRINT else None
            if LOG:
                run_log()
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>
        def is_different():
            DIFFERENT = True
            try:

                FILE_EXISTS = os.path.exists(FILENAME)
                print(f"FILE_EXISTS: {FILE_EXISTS}") if PRINT else None
                if not FILE_EXISTS:
                    DIFFERENT = True
                    return DIFFERENT

                else:
                    try:
                        existing = pd.read_csv(FILENAME,header=0,index_col=0)
                    except:
                        existing = pd.DataFrame()

                    print(f"existing len: {len(existing)}") if PRINT else None

                    if len(IF_DIFF_COLS) > 0:
                        existing_check = existing[IF_DIFF_COLS].reset_index(drop=True)
                        data_check = data[IF_DIFF_COLS].reset_index(drop=True)
                        DIFFERENT = existing_check.equals(data_check) == False
                        print(f"Difference Check IF_DIFF_COLS \t DIFFERENT = {DIFFERENT}") if PRINT else None
                        

                    elif IF_DIFF_EXCLUDE != None:
                        print(f"Difference Check Excluding '{IF_DIFF_EXCLUDE}'") if PRINT else None
                        existing_check = existing.drop([IF_DIFF_EXCLUDE], axis=1, errors='ignore')
                        new_check = data.drop([IF_DIFF_EXCLUDE], axis=1, errors='ignore')
                        DIFFERENT = new_check.equals(existing_check) == False

                    else:
                        print(f"EQUALS: {data.equals(existing)}") if PRINT else None
                        DIFFERENT = data.equals(existing) == False

            except:
                pass

            print(f"IS_DIFFERENT = {DIFFERENT}") if PRINT else None
            return DIFFERENT
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>

        IF_DIFFERENT = True if (len(IF_DIFF_COLS) > 0) or (IF_DIFF_EXCLUDE != None) else IF_DIFFERENT

        try:
            data = pd.DataFrame(data)
            if not APPEND:
                if not IF_DIFFERENT:
                    export(data,FILENAME)
                else:
                    if is_different():
                        export(data,FILENAME)
                
            elif APPEND:

                try:
                    existing = Drct.csv_from(FILENAME)
                except:
                    existing = pd.DataFrame()

                if len(existing) >0:
                    data = data.append(existing,ignore_index=True)
                    data = data.drop_duplicates()
                if not IF_DIFFERENT:
                    export(data,FILENAME)
                else:
                    if is_different():
                        export(data,FILENAME)
                print(f"Appended: {FILENAME}") if PRINT else None
        except:
            try:
                FILE = str(FILENAME).split('/')[-1]
                CREATE_FOLDER = str(FILENAME).split(FILE)[0][:-1]
                os.makedirs(CREATE_FOLDER)
                if not IF_DIFFERENT:
                    export(data,FILENAME)
                else:
                    if is_different():
                        export(data,FILENAME)
                print(f"\nCreated Missing Folder: {CREATE_FOLDER}\n") if PRINT else None
            except:
                print(f"\nCSV Export Failed: {CREATE_FOLDER}\n")
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def create_folder(FOLDER):
        count = 0
        while True:
            count = count+1
            try:
                os.makedirs(FOLDER) if not os.path.exists(FOLDER) else None
            except:
                pass
            FOLDER_EXISTS = os.path.exists(FOLDER)
            if FOLDER_EXISTS:
                break
            else:
                if count > 10:
                    print(f"create_folder() Failed. Try again in 1 second...")
                t.sleep(.5)
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def delete_folder(FOLDER,RE_CREATE=True):
        count = 0
        while True:
            count = count+1
            try:
                shutil.rmtree(FOLDER)
            except:
                pass
            FOLDER_EXISTS = os.path.exists(FOLDER)
            if not FOLDER_EXISTS:
                break
            else:
                if count > 10:
                    print(f"delete_folder() Failed. Try again in 1 second...")
                t.sleep(.5)
        if RE_CREATE:
            Drct.create_folder(FOLDER)
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def load_pcode(PCODE=None,AGG=None,PP=False,FILLED=True,UNFILLED=False,LAST_MO_ID=None,MONTHS_BACK=-1,PRINT=False):
        
        ### Get Date Period
        ##########################################
        LAST_MO_ID = datetime.now().strftime('%Y_%m') if str(LAST_MO_ID).lower() == 'now' else LAST_MO_ID
        MO_IDS = Periods.lookback_df(LB_MONTHS=12,NEXT=True)
        if LAST_MO_ID != None:
            MO_IDS = MO_IDS[(MO_IDS["month_id"] <= LAST_MO_ID)]
        MO_IDS = MO_IDS[['month_id']][:MONTHS_BACK].reset_index(drop=True)
        MO_IDS = list(MO_IDS["month_id"].unique())

        ### Folders
        ##########################################
        FILLED_FOLDER = f"{WD}Sources/aggs/{AGG}/Results/Patterns_Filled"
        UNFILLED_FOLDER = f"{WD}Sources/aggs/{AGG}/Results/Patterns_Unfilled"
        PP_FOLDER = f"{WD}Sources/aggs/{AGG}/Results/Patterns_PP"

        ### Load Pre-Processed
        ##########################################
        if PP:
            data = pd.DataFrame()
            months_found = 0
            for MONTH_ID in MO_IDS:
                CSV_PATH = f"{PP_FOLDER}/{PCODE}/{MONTH_ID}.csv"
                each = Drct.csv_from(CSV_PATH)
                if len(each) > 0:
                    months_found = months_found+1
                    data = pd.concat([data, each])
            if len(data) > 0:
                data = data.sort_values(by=['_UTILITY_puid',], ascending=[True]).reset_index(drop=True)
            if PRINT:
                DATE_MIN = pd.to_datetime(data['_UTILITY_date']).min().strftime('%Y-%m-%d')
                DATE_MAX = pd.to_datetime(data['_UTILITY_date']).max().strftime('%Y-%m-%d')
                print(f"{PCODE} \t Pre-Processed \t\t {months_found} Months \t {DATE_MIN} to {DATE_MAX} \t Len: {len(data):,.0f} \t Cols: {data.shape[1]}")
            return data

        ### Load Filled
        ##########################################
        filled = pd.DataFrame()
        months_found_filled = 0
        if FILLED:
            for MONTH_ID in MO_IDS:
                CSV_PATH = f"{FILLED_FOLDER}/{PCODE}/{MONTH_ID}.csv"
                each = Drct.csv_from(CSV_PATH)
                if len(each) > 0:
                    months_found_filled = months_found_filled+1
                    filled = pd.concat([filled, each])


        ### Load Filled
        ##########################################
        unfilled = pd.DataFrame()
        months_found_unfilled = 0
        if UNFILLED:
            for MONTH_ID in MO_IDS:
                CSV_PATH = f"{UNFILLED_FOLDER}/{PCODE}/{MONTH_ID}.csv"
                each = Drct.csv_from(CSV_PATH)
                if len(each) > 0:
                    months_found_unfilled = months_found_unfilled+1
                    unfilled = pd.concat([unfilled, each])

        ### Combine
        ##########################################
        data = pd.DataFrame()
        months_found = max(months_found_unfilled,months_found_filled)
        data = pd.concat([unfilled, filled])
        if len(data) == 0:
            print(f"{PCODE} \t NO Data Found!") if PRINT else None
            return data

        data = data.sort_values(by=['puid','data_fetch',], ascending=[True,True])
        data = data.drop_duplicates(['puid',], keep='last')
        data = data.sort_values(by=['datetime',], ascending=[True]).reset_index(drop=True)

        if PRINT:
            PRINT_TXT = ''
            if FILLED and UNFILLED:
                PRINT_TXT = 'Filled/Unfilled'
            elif FILLED:
                PRINT_TXT = 'Filled Patterns'
            elif UNFILLED:
                PRINT_TXT = 'Unfilled Patterns'

            DATE_MIN = pd.to_datetime(data['date']).min().strftime('%Y-%m-%d')
            DATE_MAX = pd.to_datetime(data['date']).max().strftime('%Y-%m-%d')
            print(f"{PCODE} \t {PRINT_TXT} \t {months_found} Months \t {DATE_MIN} to {DATE_MAX} \t Len: {len(data):,.0f} \t Cols: {data.shape[1]}")
        
        return data
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# =======================================================================


# =======================================================================
class Periods:

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def get_calendar(INCLUDE_TIMES=False,START=None,END=None,FORWARD_DAYS=None):

        CSV_CALENDAR = f"{WD}Sources/aggs/Support/calendar/All_Dates.csv"
        data = Drct.csv_from(CSV_CALENDAR)
        TODAY = datetime.now().strftime('%Y-%m-%d')
        START = TODAY if str(START).lower() == 'today' else START
        END = TODAY if str(END).lower() == 'today' else END

        if not INCLUDE_TIMES:
            data = data[['date']]

        if START != None:
            START = pd.to_datetime(START).strftime('%Y-%m-%d')
            data = Periods.cutdates(data,CUT_COL='date',START=START,END=None,RESET_INDEX=True)
        if END != None:
            END = pd.to_datetime(END).strftime('%Y-%m-%d')
            data = Periods.cutdates(data,CUT_COL='date',START=None,END=END,RESET_INDEX=True)

        if FORWARD_DAYS != None:
            data = data[:FORWARD_DAYS]

        return data
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def cutdates(data,CUT_COL='date',START=None,END=None,RESET_INDEX=False):

        data = pd.DataFrame(data)
        data[CUT_COL] = pd.to_datetime(data[CUT_COL])
        if START != None:
            mask = (data[CUT_COL] >= START)
            data = data.loc[mask]
        if END != None:
            mask = (data[CUT_COL] <= END)
            data = data.loc[mask]
        if CUT_COL == 'date':
            data['date'] = pd.to_datetime(data['date']).dt.strftime("%Y-%m-%d")
        if RESET_INDEX:
            data = data.reset_index(drop=True)
        
        return data
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def lookback_df_create(LB_MONTHS=12,NEXT=False,MIN_DATE=None,END_DATE=None,MAX=None,LB_MIN_DATE=None):

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        def first_day_of_next_month(dt):
            dt = pd.to_datetime(dt)
            if dt.month == 12:
                DATE = datetime(year=dt.year+1,month=1,day=1,tzinfo=dt.tzinfo)
            else:
                DATE = datetime(year=dt.year,month=dt.month+1,day=1,tzinfo=dt.tzinfo)
            DATE = pd.to_datetime(DATE).strftime('%Y-%m-%d')
            return DATE
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        TODAY = datetime.now().strftime('%Y-%m-%d')
        if END_DATE != None:
            END_DATE = pd.to_datetime(END_DATE).strftime('%Y-%m-%d')
        else:
            END_DATE = TODAY
            if NEXT:
                market_date = Periods.get_calendar(INCLUDE_TIMES=False,START=None,END='today',FORWARD_DAYS=None)
                market_date_mo = pd.to_datetime(market_date['date'].iloc[-1]).strftime('%m')
                now_mo = datetime.now().strftime('%m')
                if market_date_mo == now_mo and datetime.now().day > 1:
                    END_DATE = first_day_of_next_month(TODAY)

        MIN_DATE_BACKUP = '2010-01-01'
        MIN_DATE = MIN_DATE_BACKUP if MIN_DATE == None else MIN_DATE
        MIN_DATE = pd.to_datetime(MIN_DATE)
        
        CSV_CALENDAR = f"{WD}Sources/aggs/Support/calendar/All_Dates.csv"
        days = Drct.csv_from(CSV_CALENDAR)
        days = Periods.cutdates(days,CUT_COL='date',END=END_DATE,RESET_INDEX=True)


        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        def lookback_dates(DATE,LOOKBACK_MO=None):

            data = pd.DataFrame()

            RUNNING_DATE = pd.to_datetime(DATE)
            YEAR = RUNNING_DATE.year
            MONTH = RUNNING_DATE.month
            MONTH_last_day = calendar.monthrange(YEAR, MONTH)[1]

            backtest_start = datetime(YEAR,MONTH,1)
            backtest_end = datetime(YEAR,MONTH,MONTH_last_day)
            lookback_end = backtest_start - timedelta(days=1)
            lookback_start = datetime(YEAR,MONTH,1)
            lookback_prep = (lookback_end - relativedelta(months=+LOOKBACK_MO)) + timedelta(days=1)
            lookback_start = datetime(lookback_prep.year,lookback_prep.month,1)
            lookback_id = backtest_start.strftime('%Y_%m') + '_m' + str(LOOKBACK_MO)
            month_id = backtest_start.strftime('%Y_%m')
            next_date = (backtest_start - relativedelta(months=+1)) + timedelta(days=0)
            

            raw = {
            'lookback_id': [lookback_id],
            'month_id': [month_id],
            'lookback_start': [lookback_start],
            'lookback_end': [lookback_end],
            'backtest_start': [backtest_start],
            'backtest_end': [backtest_end],
            'lookback_months': [LOOKBACK_MO],
            }
            data = pd.DataFrame(data=raw)

            return data,next_date,backtest_start
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        def create_lookback_period():

            DATE = pd.to_datetime(days['date'].iloc[-1])
            count = 0
            data = pd.DataFrame()

            while True:
                each,next_date,backtest_start = lookback_dates(DATE,LOOKBACK_MO=LB_MONTHS)
                data = data.append(each,ignore_index=True)
                DATE = next_date
                count = count + 1
                if backtest_start <= MIN_DATE:
                    return data
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        data = create_lookback_period()
        data = data.sort_values(by=["lookback_months", "lookback_start",], ascending=[False, False]).reset_index(drop=True)
        if LB_MIN_DATE != None:
            LB_MIN_DATE = pd.to_datetime(LB_MIN_DATE).strftime('%Y-%m-%d')
            data = Periods.cutdates(data,CUT_COL='lookback_start',START=LB_MIN_DATE,RESET_INDEX=True)

        if MAX != None and MAX > 0:
            data = data[:MAX]
        return data
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def lookback_df(LB_MONTHS=12,NEXT=False,MIN_DATE=None,MAX=None,LB_MIN_DATE=None):

        FILENAME = f"{datetime.now().strftime('%Y_%m')}_m{LB_MONTHS}"
        CSV_FILE = f'{WD}Sources/settings/lookback_dates/{FILENAME}.csv'
        if not os.path.exists(CSV_FILE):
            CREATE_END = (datetime.now() + timedelta(days = 45)).strftime("%Y-%m-%d")
            data = Periods.lookback_df_create(LB_MONTHS=LB_MONTHS,END_DATE=CREATE_END)
            Drct.csv_to(data,CSV_FILE)
        else:
            data = Drct.csv_from(CSV_FILE)

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        def first_day_of_next_month(dt):
            dt = pd.to_datetime(dt)
            if dt.month == 12:
                DATE = datetime(year=dt.year+1,month=1,day=1,tzinfo=dt.tzinfo)
            else:
                DATE = datetime(year=dt.year,month=dt.month+1,day=1,tzinfo=dt.tzinfo)
            DATE = pd.to_datetime(DATE).strftime('%Y-%m-%d')
            return DATE
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        TODAY = datetime.now().strftime('%Y-%m-%d')
        END_DATE = TODAY
        if NEXT:
            market_date = Periods.get_calendar(INCLUDE_TIMES=False,START=None,END='today',FORWARD_DAYS=None)
            market_date_mo = pd.to_datetime(market_date['date'].iloc[-1]).strftime('%m')
            now_mo = datetime.now().strftime('%m')
            if market_date_mo == now_mo and datetime.now().day > 1:
                END_DATE = first_day_of_next_month(TODAY)

        MIN_DATE_BACKUP = '2010-01-01'
        MIN_DATE = MIN_DATE_BACKUP if MIN_DATE == None else MIN_DATE
        MIN_DATE = pd.to_datetime(MIN_DATE)
        
        data = Periods.cutdates(data,CUT_COL='backtest_start',START=MIN_DATE,RESET_INDEX=True)
        data = Periods.cutdates(data,CUT_COL='backtest_start',END=END_DATE,RESET_INDEX=True)
        
        if LB_MIN_DATE != None:
            LB_MIN_DATE = pd.to_datetime(LB_MIN_DATE).strftime('%Y-%m-%d')
            data = Periods.cutdates(data,CUT_COL='lookback_start',START=LB_MIN_DATE,RESET_INDEX=True)

        if MAX != None and MAX > 0:
            data = data[:MAX]

        data['lookback_start'] = pd.to_datetime(data['lookback_start'])
        data['lookback_end'] = pd.to_datetime(data['lookback_end'])
        data['backtest_start'] = pd.to_datetime(data['backtest_start'])
        data['backtest_end'] = pd.to_datetime(data['backtest_end'])

        return data
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# =======================================================================
