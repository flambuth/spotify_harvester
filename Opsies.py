'''
This should be the library of functions that are run in a job.
This will import from:
    Spotifies
    Databasies
Those files should not import from this. This module should wield objects from each imported library, at each other

1 Daily Job(s)
    new daily_artists*tracks every 24 hrs

    combs the latest insert for artists not in Artist Catalog
        -should only need import from Databasies
2 Recently_Played
    15 minute job checking the sp.current_user_recently_played
    spotifies.recently_played >> databasies.new_recently_played


'''
from Spotifies import daily_insert
from Databasies import Daily_Table, Artist_Catalog
from Initialize import Origin_Story
#what happened!

def initialize_tables():
    '''
    Run this once to get this thing started.
    '''
    Origin_Story().initialize()
    print('all tables finished')

def update_daily_table(table):
    '''
    This should update one of the two daily tables.

    Everytime the daily table is updated, the new daily is scanned
    for artists IDs that have not found in the artist catalog
    These art_ids added.
    '''
    work_table = Daily_Table(table)
    new_daily = daily_insert(table).daily_book
    art_cat = Artist_Catalog()

    #art_ids in the new_daily top 10 chart, so 10 art_ids
    check_this = [i['art_id'] for i in new_daily]
    are_they = art_cat.check_in_back(check_this)

    if art_cat.check_in_back(check_this):
       art_cat.add_new_arts_from_daily(are_they)

    work_table.insert_new_daily(new_daily)

def daily_update_job():
    update_daily_table('daily_artists')
    update_daily_table('daily_tracks')
    print('Daily Job completed')
