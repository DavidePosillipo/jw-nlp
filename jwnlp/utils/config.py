import logging
import os

class Config:

    base_url_root =  'https://wol.jw.org'
    watchtower_url = '/wol/library/r1/lp-e/all-publications/watchtower'

    database_name = 'debug_3'
    user_name = 'super'

    # pythonanywhere database address
    database_address = 'dp797-2402.postgres.pythonanywhere-services.com' 
    database_port = '12402'

    # ONLY FOR DEBUG TODO MOVE TO BETTER PLACE
    database_password = 'admin963'
    
    db_uri = "postgresql+psycopg2://" + user_name + ":" + database_password + "@" + database_address + ":" + database_port + "/" + database_name 
