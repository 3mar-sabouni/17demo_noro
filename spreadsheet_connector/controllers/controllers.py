import json 
import logging 
import datetime 
from odoo import http 
from odoo .http import request ,Response 
from itertools import groupby 
from odoo .tools import date_utils 
from odoo .addons .spreadsheet_connector .controllers .validate_token import validate_token 
from odoo .addons .spreadsheet_connector .common import datefields_extracter 
from math import ceil 
_OOOO000O0OO000OO0 =logging .getLogger (__name__ )
class SqlConnector (http .Controller ):
    ""
    @http .route ('/sql/tablenames/',type ='http',auth ="none",methods =['GET','OPTIONS'],csrf =False ,cors ='*')
    def get_model_names (O00000O0O00OO0O00 ,**OO0OOO000O000O000 ):
        ""
        _OOOO000O0OO000OO0 .info ('getting database tables')
        O0O00O0O0OOO0OOO0 =[]
        try :
            with http .request .env .cr .savepoint ():
                OOO000000OO0OOO0O =request .env .cr .execute ('''SELECT 
                                                    relname AS table  
                                                    FROM 
                                                    pg_stat_user_tables 
                                                    ORDER BY relname
                                                    ''')
                OOO000000OO0OOO0O =request .env .cr .dictfetchall ()
                for O0OOOOOO000OOOOO0 in OOO000000OO0OOO0O :
                    O0O00O0O0OOO0OOO0 .append (O0OOOOOO000OOOOO0 ['table'].replace ('_','.'))
        except Exception as OO000O000000OO000 :
            _OOOO000O0OO000OO0 .error (str (OO000O000000OO000 ))
            return Response (json .dumps ({'error':f'{OO000O000000OO000}'},default =date_utils .json_default ),content_type ='application/json',status =500 )
        _OOOO000O0OO000OO0 .info ('tables collection done')
        return Response (json .dumps (O0O00O0O0OOO0OOO0 ,default =date_utils .json_default ),content_type ='application/json',status =200 )
    @validate_token 
    @http .route (['/sql/connector/<string:model>','/sql/connector/<string:model>/'],type ='http',auth ="none",methods =['GET','OPTIONS'],website =True ,csrf =False ,cors ='*')
    def get_modeldate (O0O0000OOOOOOOOOO ,model ,**OOO00000OOO000O00 ):
        ""
        _OOOO000O0OO000OO0 .info (f'getting data of {model} ')
        O0O00OO0000O00OO0 =200 
        OO0OOOO0OO0OO00O0 =request .env ['ir.config_parameter'].sudo ().get_param ('web.base.url')
        O0O00O0OOO0OO0000 =False 
        try :
            request .env .cr .execute (f'''
                                SELECT
                                COUNT(*) AS size
                                FROM
                                {model.replace('.', '_')}
                                ''')
            O0O00O0OOO0OO0000 =request .env .cr .dictfetchall ()[0 ]['size']
        except Exception as O000OO00OO0O00OOO :
            _OOOO000O0OO000OO0 .error (str (O000OO00OO0O00OOO ))
            OOOO0O0O0000000O0 ={'error':str (O000OO00OO0O00OOO )}
            O0O00OO0000O00OO0 =500 
            return Response (json .dumps (OOOO0O0O0000000O0 ,default =date_utils .json_default ),content_type ='application/json',status =O0O00OO0000O00OO0 )
        OOOO0O0O0000000O0 ={"count":int (OOO00000OOO000O00 .get ('count',20000 )),"prev":None ,"current":int (OOO00000OOO000O00 .get ('current',1 )),"next":None ,"total_pages":None ,"data":[],"size":O0O00O0OOO0OO0000 }
        OOOO0O0O0000000O0 ['total_pages']=ceil (O0O00O0OOO0OO0000 /OOOO0O0O0000000O0 .get ('count'))
        OOOO0O0O0000000O0 ['next']=None if OOOO0O0O0000000O0 .get ('current')==OOOO0O0O0000000O0 .get ('total_pages')or OOOO0O0O0000000O0 .get ('total_pages')==0 else OO0OOOO0OO0OO00O0 +'/sql/connector/'+model +'?current='+str (OOOO0O0O0000000O0 .get ('current')+1 )
        OOOO0O0O0000000O0 ['prev']=None if OOOO0O0O0000000O0 .get ('current')==1 else OO0OOOO0OO0OO00O0 +'/sql/connector/'+model +'?current='+str (OOOO0O0O0000000O0 .get ('current')-1 )
        if not OOOO0O0O0000000O0 .get ('prev',False ):
            OOOO0O0O0000000O0 .pop ('prev')
        if not OOOO0O0O0000000O0 .get ('next',False ):
            OOOO0O0O0000000O0 .pop ('next')
        OO0OO0O0OOO0OO00O =OOOO0O0O0000000O0 .get ('current')*OOOO0O0O0000000O0 .get ('count')
        OOO000OOOO0000O0O =OO0OO0O0OOO0OO00O -OOOO0O0O0000000O0 .get ('count')
        if not OOOO0O0O0000000O0 .get ('total_pages',False ):
            OOOO0O0O0000000O0 .pop ('current')
        try :
            with http .request .env .cr .savepoint ():
                OOOO00O0OOO00OOOO =request .env .cr .execute (f'''
                                                SELECT *
                                                FROM
                                                {model.replace('.', '_')}
                                                LIMIT {OOOO0O0O0000000O0.get('count')} OFFSET {OOO000OOOO0000O0O} ''')
                OOOO00O0OOO00OOOO =request .env .cr .dictfetchall ()
                for OO00O0OOOO0O00O00 in OOOO00O0OOO00OOOO :
                    for OOOO0OOO0OO00O0OO ,OOO0OOO0OOO0OO0OO in OO00O0OOOO0O00O00 .items ():
                        if isinstance (OOO0OOO0OOO0OO0OO ,datetime .datetime ):
                            OO00O0OOOO0O00O00 [OOOO0OOO0OO00O0OO ]=OOO0OOO0OOO0OO0OO .strftime ("%Y%m%d%H%M%S")
                OOOO0O0O0000000O0 ['data']=OOOO00O0OOO00OOOO 
        except Exception as O000OO00OO0O00OOO :
            print ("except")
            _OOOO000O0OO000OO0 .error (str (O000OO00OO0O00OOO ))
            OOOO0O0O0000000O0 ['data']=[]
            O0O00OO0000O00OO0 =200 
        return Response (json .dumps (OOOO0O0O0000000O0 ,default =date_utils .json_default ),content_type ='application/json',status =O0O00OO0000O00OO0 )
