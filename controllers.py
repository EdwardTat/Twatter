"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

import datetime
import random


from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_username, get_user


url_signer = URLSigner(session)

# Some constants.
MAX_RETURNED_USERS = 20 # Our searches do not return more than 20 users.
MAX_RESULTS = 20 # Maximum number of returned meows. 

@action('index')
@action.uses('index.html', db, auth.user, url_signer)
def index():
    return dict(
        # COMPLETE: return here any signed URLs you need.
        post_new_meow_url=URL('post_new_meow', signer=url_signer),
        get_users_url = URL('get_users', signer=url_signer),
        follow_url=URL('set_follow', signer=url_signer),
        get_recent_meows_url = URL('get_recent_meows', signer=url_signer),
        get_feed_meows_url = URL('get_feed_meows', signer=url_signer),
        get_your_meows_url = URL('get_your_meows', signer=url_signer),
        get_user_p_url = URL('get_user_p', signer=url_signer),
        get_replies_url = URL('get_replies', signer=url_signer),
        post_new_reply_url = URL('post_new_reply', signer=url_signer),
        
    )
    
@action("get_replies")
@action.uses(db, auth.user)
def get_replies():
    temp = request.params.get('id')
    assert temp is not None
    pviews = db(db.meows.replyID == 
                temp).select(orderby=~db.meows.id, limitby=(0, 5))
    print("pviews = ")
    print(pviews)
    return dict(posts = pviews)
    
@action("get_user_p")
@action.uses(db, auth.user)
def get_user_p():
    temp = request.params.get('id')
    assert temp is not None
    pviews = db(db.meows.username == temp).select(orderby=~db.meows.id, limitby=(0, 5))
    return dict(posts = pviews)
    
@action("get_feed_meows")
@action.uses(db, auth.user)
def get_feed_meows():  
    temp = db(((db.flist.user == get_username()) & (db.flist.status == True))).select()
    temp2 = [a.following for a in temp]
    pviews = db(db.meows.username.belongs(temp2)).select(orderby=~db.meows.id, limitby=(0, 5))
#    pviews = db(db.meows).select(orderby=~db.meows.id, limitby=(0, 5))
    return dict(posts = pviews)

    
@action("get_recent_meows")
@action.uses(db, auth.user)
def get_recent_meows():
    print("called\n\n\n")
    #pviews = db(db.meows).select()
    pviews = db(db.meows).select(orderby=~db.meows.id, limitby=(0, 5))
    return dict(posts = pviews)

@action("get_your_meows")
@action.uses(db, auth.user)
def get_your_meows():
    print("called\n\n\n")
    #pviews = db(db.meows).select()
    #pviews = db(db.meows).select(orderby=~db.meows.id, limitby=(0, 5))
    pviews = db(db.meows.username == get_username()).select(orderby=~db.meows.id, limitby=(0, 5))
    return dict(posts = pviews)



@action("post_new_reply")
@action.uses(db, auth.user)
def post_new_reply():
    temp = request.params.get('x')
    id = request.params.get('id')
    person = db(db.meows.id == id).select().first()
    print("person = ")
    print(person)
    
    db(db.meows.id == id).update(rn = person.rn + 1)
    
    db.meows.insert(replyID = id, post = temp, username = get_username(),
                      rn = 0, timestamp = datetime.datetime.now().isoformat())
    
    return dict()

@action("post_new_meow")
@action.uses(db, auth.user)
def post_new_meow():
    temp = request.params.get('q')
    db.meows.insert(post = temp, username = get_username(),
                    rn = 0, timestamp = datetime.datetime.now().isoformat(),
                    replyID = 0)
    return dict()

@action("get_users")
@action.uses(db, auth.user)
def get_users():
    # Implement. 
    
    temp = db(db.auth_user.username != get_username()).select()
    
    for i in temp:
        if((db((db.flist.user == get_username()) & (db.flist.following == i.username)).isempty())):
            db.flist.insert(user = get_username(), following = i.username, status = False)
    
    temp2 = db(db.flist).select()
    
    for i in temp2:
        if(db(db.auth_user.username == i.user).isempty() or 
           db(db.auth_user.username == i.following).isempty()):
            db((db.flist.user == i.user) & (db.flist.following == i.following) & (db.flist.status == i.status)).delete()
    
    t = request.params.get('q')
    if t:
        tt = t.strip()
        users = db(((db.flist.user == get_username()) & (db.flist.following.startswith(tt)) & (db.flist.status == True))).select()
        users2 = db(((db.flist.user == get_username()) & (db.flist.following.startswith(tt)) & (db.flist.status == False))).select()
    else:
        users = db((db.flist.user == get_username()) & (db.flist.status == True)).select()
        users2 = db((db.flist.user == get_username()) & (db.flist.status == False)).select()
    
    
    return dict(users = users, users2 = users2)


@action("set_follow")
@action.uses(db, auth.user)
def set_follow():
    # Implement. 
    
    temp = request.params.get('id')
    assert temp is not None
    switch = db((db.flist.following == temp) & (db.flist.user == get_username())).select().first().id
    st = db((db.flist.following == temp) & (db.flist.user == get_username())).select().first().status
    if(st == "False"):
        db(db.flist.id == switch).update(status = True)
    else:
        db(db.flist.id == switch).update(status = False)
        
    return "ok"
